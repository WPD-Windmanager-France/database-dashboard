import { redirect, type Handle } from '@sveltejs/kit';

export const handle: Handle = async ({ event, resolve }) => {
	// Cloudflare Access headers
	const email = event.request.headers.get('cf-access-authenticated-user-email');
	const commonName = event.request.headers.get('cf-access-authenticated-user-common-name');
	
	// Mock logic for local development
	const isDev = process.env.NODE_ENV === 'development';
	const mockEmail = process.env.DEV_MOCK_EMAIL || 'dev@wpd.fr';
	
	if (!email && isDev) {
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
		event.locals.user = null;
	}

	const response = await resolve(event);
	return response;
};
