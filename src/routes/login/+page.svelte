<script lang="ts">
	import { createBrowserClient } from '@supabase/ssr';
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';

	export let data;

	let email = '';
	let password = '';
	let error = '';
	let success = '';
	let loading = false;
	let mode: 'login' | 'signup' = 'login';

	// Check for error from URL params (e.g. domain restriction)
	$: {
		const errorParam = $page.url.searchParams.get('error');
		if (errorParam === 'domain') {
			error = "Accès restreint aux comptes @wpd.fr.";
		}
	}

	async function handleLogin() {
		if (!email || !password) {
			error = "Veuillez remplir tous les champs.";
			return;
		}

		loading = true;
		error = '';
		success = '';

		const supabase = createBrowserClient(data.supabaseUrl, data.supabaseAnonKey);

		const { error: authError } = await supabase.auth.signInWithPassword({
			email,
			password
		});

		if (authError) {
			if (authError.message.includes('Invalid login credentials')) {
				error = "Email ou mot de passe incorrect.";
			} else if (authError.message.includes('Email not confirmed')) {
				error = "Veuillez confirmer votre email avant de vous connecter.";
			} else {
				error = authError.message;
			}
			loading = false;
		} else {
			goto('/dashboard');
		}
	}

	async function handleSignup() {
		if (!email || !password) {
			error = "Veuillez remplir tous les champs.";
			return;
		}
		if (!email.endsWith('@wpd.fr')) {
			error = "Seuls les emails @wpd.fr sont autorisés.";
			return;
		}
		if (password.length < 6) {
			error = "Le mot de passe doit contenir au moins 6 caractères.";
			return;
		}

		loading = true;
		error = '';
		success = '';

		const supabase = createBrowserClient(data.supabaseUrl, data.supabaseAnonKey);

		const { error: authError } = await supabase.auth.signUp({
			email,
			password
		});

		if (authError) {
			if (authError.message.includes('already registered')) {
				error = "Cet email est déjà inscrit.";
			} else {
				error = authError.message;
			}
		} else {
			success = "Compte créé ! Vérifiez votre email pour confirmer, puis connectez-vous.";
			mode = 'login';
		}
		loading = false;
	}
</script>

<svelte:head>
	<title>Connexion — WNDMNGR</title>
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-50 to-gray-100">
	<div class="bg-white rounded-xl shadow-lg p-8 max-w-md w-full mx-4">
		<div class="mb-6 text-center">
			<h1 class="text-2xl font-bold text-gray-800">WNDMNGR</h1>
			<p class="text-sm text-gray-500 mt-1">Wind Farm Management Dashboard</p>
		</div>

		{#if error}
			<div class="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
				<p class="text-red-700 text-sm">{error}</p>
			</div>
		{/if}

		{#if success}
			<div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
				<p class="text-green-700 text-sm">{success}</p>
			</div>
		{/if}

		<form on:submit|preventDefault={mode === 'login' ? handleLogin : handleSignup} class="space-y-4">
			<div>
				<label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
				<input
					id="email"
					type="email"
					bind:value={email}
					placeholder="prenom.nom@wpd.fr"
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1565c0] focus:border-transparent outline-none"
					disabled={loading}
				/>
			</div>

			<div>
				<label for="password" class="block text-sm font-medium text-gray-700 mb-1">Mot de passe</label>
				<input
					id="password"
					type="password"
					bind:value={password}
					placeholder="••••••••"
					class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#1565c0] focus:border-transparent outline-none"
					disabled={loading}
				/>
			</div>

			<button
				type="submit"
				class="w-full bg-[#1565c0] hover:bg-[#0d47a1] text-white font-medium py-3 px-6 rounded-lg transition-colors disabled:opacity-50"
				disabled={loading}
			>
				{#if loading}
					Chargement...
				{:else if mode === 'login'}
					Se connecter
				{:else}
					Créer le compte
				{/if}
			</button>
		</form>

		<div class="mt-4 text-center">
			{#if mode === 'login'}
				<button
					on:click={() => { mode = 'signup'; error = ''; success = ''; }}
					class="text-sm text-[#1565c0] hover:underline"
				>
					Pas de compte ? Créer un compte
				</button>
			{:else}
				<button
					on:click={() => { mode = 'login'; error = ''; success = ''; }}
					class="text-sm text-[#1565c0] hover:underline"
				>
					Déjà un compte ? Se connecter
				</button>
			{/if}
		</div>
	</div>
</div>
