import { type Handle, redirect } from '@sveltejs/kit';
import { dev } from '$app/environment';
import { env } from '$env/dynamic/private';
import { createServerClient } from '@supabase/ssr';

export const handle: Handle = async ({ event, resolve }) => {
	// --- DEV MOCK: skip Supabase Auth entirely in local dev ---
	if (dev) {
		const mockEmail = env.DEV_MOCK_EMAIL || 'dev@wpd.fr';
		event.locals.user = {
			email: mockEmail,
			name: mockEmail.split('@')[0]
		};
		return resolve(event);
	}

	// --- PRODUCTION: Supabase Auth via @supabase/ssr ---
	const supabaseUrl = env.SUPABASE_URL;
	const supabaseAnonKey = env.SUPABASE_ANON_KEY;

	if (!supabaseUrl || !supabaseAnonKey) {
		throw new Error('Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables');
	}

	event.locals.supabase = createServerClient(supabaseUrl, supabaseAnonKey, {
		cookies: {
			getAll: () => event.cookies.getAll(),
			setAll: (cookies) => {
				cookies.forEach(({ name, value, options }) => {
					event.cookies.set(name, value, { ...options, path: '/' });
				});
			}
		}
	});

	// Convenience helper that validates the session server-side
	event.locals.safeGetSession = async () => {
		const { data: { user }, error } = await event.locals.supabase.auth.getUser();
		if (error || !user) {
			return { session: null, user: null };
		}
		const { data: { session } } = await event.locals.supabase.auth.getSession();
		return { session, user };
	};

	// Validate session and populate locals.user
	const { user: authUser } = await event.locals.safeGetSession();

	if (authUser?.email) {
		// Domain restriction: @wpd.fr only
		if (!authUser.email.endsWith('@wpd.fr')) {
			await event.locals.supabase.auth.signOut();
			event.locals.user = null;
			if (event.url.pathname.startsWith('/api')) {
				return new Response(JSON.stringify({ error: 'Access restricted to wpd.fr domain' }), {
					status: 403,
					headers: { 'Content-Type': 'application/json' }
				});
			}
			redirect(303, '/login?error=domain');
		}

		event.locals.user = {
			email: authUser.email,
			name: authUser.user_metadata?.full_name || authUser.user_metadata?.name || authUser.email.split('@')[0]
		};
	} else {
		event.locals.user = null;

		// Route protection
		if (event.url.pathname.startsWith('/api')) {
			return new Response(JSON.stringify({ error: 'Unauthorized – authentication required' }), {
				status: 401,
				headers: { 'Content-Type': 'application/json' }
			});
		}
		if (event.url.pathname.startsWith('/dashboard')) {
			redirect(303, '/login');
		}
	}

	const response = await resolve(event);
	return response;
};
