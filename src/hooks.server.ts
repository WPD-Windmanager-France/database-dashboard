import { type Handle } from '@sveltejs/kit';
import { dev } from '$app/environment';
import { env } from '$env/dynamic/private';

export const handle: Handle = async ({ event, resolve }) => {
	// Cloudflare Access headers
	const email = event.request.headers.get('cf-access-authenticated-user-email');
	const commonName = event.request.headers.get('cf-access-authenticated-user-common-name');

	// Mock logic for local development
	const mockEmail = env.DEV_MOCK_EMAIL || 'dev@wpd.fr';

	if (!email && dev) {
		event.locals.user = {
			email: mockEmail,
			name: mockEmail.split('@')[0]
		};
	} else if (email) {
		// Restrict to @wpd.fr if email exists (Production safety)
		if (!email.endsWith('@wpd.fr')) {
			return new Response('Access Restricted to wpd.fr domain', { status: 403 });
		}

		// Propagate identity to the app via locals
		event.locals.user = {
			email,
			name: commonName || email.split('@')[0]
		};
	} else {
		// PRODUCTION GUARD: No CF headers and not dev → block access entirely
		// This prevents data exposure if Cloudflare Access is misconfigured
		if (event.url.pathname.startsWith('/api') || event.url.pathname.startsWith('/dashboard')) {
			return new Response('Unauthorized – authentication required', { status: 401 });
		}
		event.locals.user = null;
	}

	const response = await resolve(event);
	return response;
};
