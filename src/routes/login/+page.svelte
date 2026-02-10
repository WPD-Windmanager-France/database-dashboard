<script lang="ts">
	import { onMount } from 'svelte';
	import { createBrowserClient } from '@supabase/ssr';
	import { page } from '$app/stores';

	export let data;

	let error = '';
	let loading = true;

	const errorMessages: Record<string, string> = {
		domain: "Accès restreint aux comptes @wpd.fr.",
		auth: "Erreur d'authentification. Veuillez réessayer.",
		callback: "Erreur lors de la connexion. Veuillez réessayer."
	};

	onMount(() => {
		const errorParam = $page.url.searchParams.get('error');
		if (errorParam) {
			error = errorMessages[errorParam] || "Une erreur est survenue.";
			loading = false;
			return;
		}

		// Auto-trigger Microsoft OAuth (seamless, like Cloudflare Access)
		triggerOAuth();
	});

	async function triggerOAuth() {
		loading = true;
		error = '';

		const supabase = createBrowserClient(data.supabaseUrl, data.supabaseAnonKey);

		const { error: oauthError } = await supabase.auth.signInWithOAuth({
			provider: 'azure',
			options: {
				scopes: 'email',
				redirectTo: `${window.location.origin}/auth/callback`
			}
		});

		if (oauthError) {
			error = oauthError.message;
			loading = false;
		}
	}
</script>

<svelte:head>
	<title>Connexion — WNDMNGR</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
	<div class="bg-white rounded-xl shadow-lg p-8 max-w-md w-full mx-4 text-center">
		<div class="mb-6">
			<h1 class="text-2xl font-bold text-gray-800">WNDMNGR</h1>
			<p class="text-sm text-gray-500 mt-1">Wind Farm Management Dashboard</p>
		</div>

		{#if loading && !error}
			<div class="py-8">
				<div class="animate-spin rounded-full h-10 w-10 border-b-2 border-[#1565c0] mx-auto"></div>
				<p class="text-gray-500 mt-4">Redirection vers Microsoft...</p>
			</div>
		{/if}

		{#if error}
			<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
				<p class="text-red-700 text-sm">{error}</p>
			</div>

			<button
				on:click={triggerOAuth}
				class="w-full flex items-center justify-center gap-3 bg-[#1565c0] hover:bg-[#0d47a1] text-white font-medium py-3 px-6 rounded-lg transition-colors"
			>
				<svg class="w-5 h-5" viewBox="0 0 21 21" fill="none">
					<rect width="10" height="10" fill="#f25022"/>
					<rect x="11" width="10" height="10" fill="#7fba00"/>
					<rect y="11" width="10" height="10" fill="#00a4ef"/>
					<rect x="11" y="11" width="10" height="10" fill="#ffb900"/>
				</svg>
				Réessayer avec Microsoft
			</button>
		{/if}
	</div>
</div>
