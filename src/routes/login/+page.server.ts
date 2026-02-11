import { redirect } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
	// If already authenticated, redirect to dashboard
	if (locals.user) {
		redirect(303, '/data');
	}

	// Pass Supabase credentials to client for OAuth trigger
	return {
		supabaseUrl: env.SUPABASE_URL || '',
		supabaseAnonKey: env.SUPABASE_ANON_KEY || ''
	};
};
