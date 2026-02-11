<script lang="ts">
	import type { PageData } from './$types';
	import FarmSelector from '$lib/components/ui/FarmSelector.svelte';
	import EditableField from '$lib/components/ui/EditableField.svelte';
	import FarmCard from '$lib/components/ui/FarmCard.svelte';
	import PerformanceChart from '$lib/components/viz/PerformanceChart.svelte';
	import StatCard from '$lib/components/viz/StatCard.svelte';

	export let data: PageData;

	const tabs = ['Dashboard', 'General', 'Referents', 'Services', 'Contracts', 'Location'] as const;
	let activeTab: (typeof tabs)[number] = 'Dashboard';

	$: fd = data.farmData;
	$: farm = fd?.farm;
	$: farmTypeOptions = (data.farmTypes ?? []).map((ft: any) => ({
		value: String(ft.id),
		label: ft.type_title
	}));

	// Referents editing state
	let editingRole = '';
	let selectedPersonUuid = '';
	let savingReferent = false;
	let showNewPerson = false;
	let newFirst = '';
	let newLast = '';

	function startEditReferent(role: string) {
		editingRole = role;
		// Find current person for this role
		const current = fd?.referents.find((r) => r.role === role);
		selectedPersonUuid = '';
		showNewPerson = false;
		newFirst = '';
		newLast = '';
	}

	function cancelEditReferent() {
		editingRole = '';
	}

	async function saveReferent() {
		if (!farm) return;
		savingReferent = true;
		try {
			const body: any = {
				role: editingRole,
				personUuid: selectedPersonUuid || null
			};
			if (showNewPerson && newFirst && newLast) {
				body.newPerson = { first_name: newFirst, last_name: newLast };
			}
			const res = await fetch(`/api/farms/${farm.uuid}/referents`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(body)
			});
			if (res.ok) {
				// Reload page to get fresh data
				window.location.reload();
			}
		} finally {
			savingReferent = false;
		}
	}

	// Contracts editing state
	let editingContractSection = '';
	let savingContract = false;

	let adminFields = {
		siret_number: '',
		vat_number: '',
		account_number: '',
		legal_representative: '',
		head_office_address: '',
		windmanager_subsidiary: ''
	};
	let omFields = { service_contract_type: '', contract_end_date: '' };
	let tcmaFields = { contract_type: '', tcma_status: '', effective_date: '', end_date: '' };
	let finGuarFields = { amount: 0, due_date: '' };
	let elecDelFields = { in_place: false, drei_date: '' };
	let envInstFields = { aip_number: '', prefecture_name: '', duty_dreal_contact: '' };

	function startEditContract(section: string) {
		editingContractSection = section;
		if (section === 'administration') {
			const a = fd?.administration;
			adminFields = {
				siret_number: a?.siret_number ?? '',
				vat_number: a?.vat_number ?? '',
				account_number: a?.account_number ?? '',
				legal_representative: a?.legal_representative ?? '',
				head_office_address: a?.head_office_address ?? '',
				windmanager_subsidiary: a?.windmanager_subsidiary ?? ''
			};
		} else if (section === 'om-contract') {
			const o = fd?.omContract;
			omFields = {
				service_contract_type: o?.service_contract_type ?? '',
				contract_end_date: o?.contract_end_date ?? ''
			};
		} else if (section === 'tcma-contract') {
			const t = fd?.tcmaContract;
			tcmaFields = {
				contract_type: t?.contract_type ?? '',
				tcma_status: t?.tcma_status ?? '',
				effective_date: t?.effective_date ?? '',
				end_date: t?.end_date ?? ''
			};
		} else if (section === 'financial-guarantee') {
			const f = fd?.financialGuarantee;
			finGuarFields = {
				amount: f?.amount ?? 0,
				due_date: f?.due_date ?? ''
			};
		} else if (section === 'electrical-delegation') {
			const e = fd?.electricalDelegation;
			elecDelFields = {
				in_place: e?.in_place ?? false,
				drei_date: e?.drei_date ?? ''
			};
		} else if (section === 'environmental-installation') {
			const ei = fd?.environmentalInstallation;
			envInstFields = {
				aip_number: ei?.aip_number ?? '',
				prefecture_name: ei?.prefecture_name ?? '',
				duty_dreal_contact: ei?.duty_dreal_contact ?? ''
			};
		}
	}

	async function saveContract() {
		if (!farm) return;
		savingContract = true;
		try {
			let body: any;
			if (editingContractSection === 'administration') body = adminFields;
			else if (editingContractSection === 'om-contract') body = omFields;
			else if (editingContractSection === 'tcma-contract') body = tcmaFields;
			else if (editingContractSection === 'financial-guarantee') body = finGuarFields;
			else if (editingContractSection === 'electrical-delegation') body = elecDelFields;
			else if (editingContractSection === 'environmental-installation') body = envInstFields;

			const res = await fetch(`/api/farms/${farm.uuid}/${editingContractSection}`, {
				method: 'PATCH',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(body)
			});
			if (res.ok) window.location.reload();
		} finally {
			savingContract = false;
		}
	}

	// Location editing
	let editingLocation = false;
	let locFields = {
		country: '',
		region: '',
		department: '',
		municipality: '',
		map_reference: '',
		arras_round_trip_distance_km: 0,
		vertou_round_trip_duration_h: 0,
		arras_toll_eur: 0,
		nantes_toll_eur: 0
	};
	let savingLocation = false;

	function startEditLocation() {
		const loc = fd?.location;
		locFields = {
			country: loc?.country ?? '',
			region: loc?.region ?? '',
			department: loc?.department ?? '',
			municipality: loc?.municipality ?? '',
			map_reference: loc?.map_reference ?? '',
			arras_round_trip_distance_km: loc?.arras_round_trip_distance_km ?? 0,
			vertou_round_trip_duration_h: loc?.vertou_round_trip_duration_h ?? 0,
			arras_toll_eur: loc?.arras_toll_eur ?? 0,
			nantes_toll_eur: loc?.nantes_toll_eur ?? 0
		};
		editingLocation = true;
	}

	async function saveLocation() {
		if (!farm) return;
		savingLocation = true;
		try {
			const res = await fetch(`/api/farms/${farm.uuid}/location`, {
				method: 'PATCH',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(locFields)
			});
			if (res.ok) {
				window.location.reload();
			}
		} finally {
			savingLocation = false;
		}
	}

	// Services (company roles) editing state
	let editingServiceRole = '';
	let selectedCompanyUuid = '';
	let savingService = false;
	let showNewCompany = false;
	let newCompanyName = '';

	function getCompanyForRole(roleName: string): { company_name: string; company_uuid: string; company_role_id: number } | null {
		const cr = fd?.companyRoles.find((c) => c.role_name === roleName);
		return cr ?? null;
	}

	function startEditService(roleName: string) {
		editingServiceRole = roleName;
		const current = getCompanyForRole(roleName);
		selectedCompanyUuid = current?.company_uuid ?? '';
		showNewCompany = false;
		newCompanyName = '';
	}

	function cancelEditService() {
		editingServiceRole = '';
	}

	async function saveService() {
		if (!farm) return;
		savingService = true;
		try {
			const current = getCompanyForRole(editingServiceRole);

			if (!selectedCompanyUuid && !showNewCompany) {
				// Remove assignment
				if (current) {
					await fetch(`/api/farms/${farm.uuid}/company-roles`, {
						method: 'DELETE',
						headers: { 'Content-Type': 'application/json' },
						body: JSON.stringify({
							companyRoleId: current.company_role_id,
							companyUuid: current.company_uuid
						})
					});
				}
			} else {
				const body: any = {
					roleName: editingServiceRole,
					companyUuid: selectedCompanyUuid,
					oldCompanyUuid: current?.company_uuid
				};
				if (showNewCompany && newCompanyName) {
					body.companyUuid = 'new';
					body.newCompany = { name: newCompanyName };
				}
				await fetch(`/api/farms/${farm.uuid}/company-roles`, {
					method: 'PUT',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(body)
				});
			}
			window.location.reload();
		} finally {
			savingService = false;
		}
	}

	// Key person roles for the Referents tab
	const personRoles = [
		'Technical Manager',
		'Key Account Manager',
		'Head of Technical Management',
		'Electrical Manager',
		'Field Crew Manager',
		'Asset Manager'
	];

	function getReferentName(role: string): string {
		return fd?.referents.find((r) => r.role === role)?.referent_name ?? 'N/A';
	}
</script>

<div class="flex min-h-screen">
	<!-- Sidebar -->
	<aside class="sidebar w-[300px] flex-shrink-0 p-5 flex flex-col">
		{#if data.user}
			<div class="bg-white rounded-lg p-4 mb-4 shadow-sm">
				<div class="text-xs text-gray-500 mb-1">Connecte en tant que</div>
				<div class="font-semibold text-sm">{data.user.name}</div>
				<div class="text-xs text-gray-500">{data.user.email}</div>
				<form method="POST" action="/api/auth/logout">
					<button
						type="submit"
						class="mt-3 w-full text-xs text-gray-500 hover:text-red-600 border border-gray-200 hover:border-red-200 rounded px-3 py-1.5 transition-colors"
					>
						Se deconnecter
					</button>
				</form>
			</div>
		{/if}

		<h3 class="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">Wind Farms</h3>

		<FarmSelector farms={data.farms} selectedUuid={data.selectedUuid} />

		<div class="mt-auto pt-4">
			<a href="/docs" class="text-xs text-gray-400 hover:text-gray-600 transition-colors">
				Database Documentation
			</a>
		</div>
	</aside>

	<!-- Main content -->
	<main class="flex-1 p-8">
		{#if farm}
			<!-- Farm header -->
			<div class="farm-title mb-6">
				<h1 class="text-2xl font-bold">{farm.project}</h1>
				<p class="text-sm opacity-75 mt-1">
					Code: {farm.code} &middot; SPV: {farm.spv} &middot; Type: {farm.farm_type}
				</p>
			</div>

			<!-- Tab bar -->
			<div class="tab-bar mb-6">
				{#each tabs as tab}
					<button
						class="tab-item {activeTab === tab ? 'active' : ''}"
						on:click={() => (activeTab = tab)}
					>
						{tab}
					</button>
				{/each}
			</div>

			<!-- TAB: Dashboard -->
			{#if activeTab === 'Dashboard'}
				<div class="grid grid-cols-3 gap-4 mb-6">
					<StatCard
						label="Turbine Count"
						value={fd?.turbineDetails?.turbine_count ?? 'N/A'}
					/>
					<StatCard
						label="Total Power"
						value={fd?.turbineDetails?.total_mmw ?? 'N/A'}
						unit="MW"
					/>
					<StatCard
						label="Farm Status"
						value={fd?.status?.farm_status ?? 'N/A'}
					/>
				</div>

				<div class="grid grid-cols-2 gap-4">
					<PerformanceChart
						actual={fd?.actualPerformances ?? []}
						target={fd?.targetPerformances ?? []}
					/>
					<div class="space-y-3">
						<FarmCard title="Turbine Details">
							{#if fd?.turbineDetails}
								<div class="grid grid-cols-2 gap-2 text-sm">
									<div>
										<span class="info-label">Manufacturer</span>
										<div class="info-value">{fd.turbineDetails.manufacturer}</div>
									</div>
									<div>
										<span class="info-label">Hub Height</span>
										<div class="info-value">{fd.turbineDetails.hub_height_m} m</div>
									</div>
									<div>
										<span class="info-label">Rotor Diameter</span>
										<div class="info-value">{fd.turbineDetails.rotor_diameter_m} m</div>
									</div>
									<div>
										<span class="info-label">Rated Power</span>
										<div class="info-value">{fd.turbineDetails.rated_power_installed_mw} MW</div>
									</div>
								</div>
							{:else}
								<p class="text-sm text-gray-400">No turbine data</p>
							{/if}
						</FarmCard>

						<FarmCard title="Status">
							<div class="grid grid-cols-2 gap-2 text-sm">
								<div>
									<span class="info-label">Farm Status</span>
									<div class="info-value">{fd?.status?.farm_status ?? 'N/A'}</div>
								</div>
								<div>
									<span class="info-label">TCMA Status</span>
									<div class="info-value">{fd?.status?.tcma_status ?? 'N/A'}</div>
								</div>
							</div>
						</FarmCard>
					</div>
				</div>

			<!-- TAB: General -->
			{:else if activeTab === 'General'}
				<h2 class="section-title">General Information</h2>
				<div class="grid grid-cols-2 gap-4">
					<div>
						<EditableField
							label="SPV"
							value={farm.spv}
							fieldName="spv"
							farmUuid={farm.uuid}
						/>
						<EditableField
							label="Project Name"
							value={farm.project}
							fieldName="project"
							farmUuid={farm.uuid}
						/>
					</div>
					<div>
						<EditableField
							label="Farm Code"
							value={farm.code}
							fieldName="code"
							farmUuid={farm.uuid}
							readonly
						/>
						<EditableField
							label="Farm Type"
							value={String(farm.farm_type_id)}
							fieldName="farm_type_id"
							farmUuid={farm.uuid}
							inputType="select"
							options={farmTypeOptions}
						/>
					</div>
				</div>

				<h2 class="section-title mt-6">Status</h2>
				<FarmCard>
					<div class="grid grid-cols-2 gap-4 text-sm">
						<div>
							<span class="info-label">Farm Status</span>
							<div class="info-value">{fd?.status?.farm_status ?? 'N/A'}</div>
						</div>
						<div>
							<span class="info-label">TCMA Status</span>
							<div class="info-value">{fd?.status?.tcma_status ?? 'N/A'}</div>
						</div>
					</div>
				</FarmCard>

			<!-- TAB: Referents -->
			{:else if activeTab === 'Referents'}
				<h2 class="section-title">Referents</h2>
				<div class="grid grid-cols-2 gap-4">
					{#each personRoles as role}
						<div class="info-card">
							<div class="info-label">{role}</div>

							{#if editingRole === role}
								<div class="mt-2 space-y-2">
									<select
										bind:value={selectedPersonUuid}
										class="w-full border rounded px-2 py-1 text-sm"
									>
										<option value="">N/A</option>
										{#each data.persons as person}
											<option value={person.uuid}>
												{person.first_name} {person.last_name}
											</option>
										{/each}
									</select>

									<button
										class="text-xs text-[var(--color-primary)] underline"
										on:click={() => (showNewPerson = !showNewPerson)}
									>
										{showNewPerson ? 'Cancel new person' : '+ New Person'}
									</button>

									{#if showNewPerson}
										<div class="flex gap-2">
											<input
												bind:value={newFirst}
												placeholder="First name"
												class="flex-1 border rounded px-2 py-1 text-sm"
											/>
											<input
												bind:value={newLast}
												placeholder="Last name"
												class="flex-1 border rounded px-2 py-1 text-sm"
											/>
										</div>
									{/if}

									<div class="flex gap-2">
										<button class="btn-primary" on:click={saveReferent} disabled={savingReferent}>
											{savingReferent ? '...' : 'Save'}
										</button>
										<button class="btn-cancel" on:click={cancelEditReferent}>Cancel</button>
									</div>
								</div>
							{:else}
								<div class="flex items-center gap-2 mt-1">
									<span class="info-value">{getReferentName(role)}</span>
									<button class="btn-edit" on:click={() => startEditReferent(role)}>Edit</button>
								</div>
							{/if}
						</div>
					{/each}
				</div>

			<!-- TAB: Services -->
			{:else if activeTab === 'Services'}
				<h2 class="section-title">Service Providers</h2>
				<div class="grid grid-cols-2 gap-4">
					{#each data.companyRoles as role}
						<div class="info-card">
							<div class="info-label">{role.role_name}</div>

							{#if editingServiceRole === role.role_name}
								<div class="mt-2 space-y-2">
									<select
										bind:value={selectedCompanyUuid}
										class="w-full border rounded px-2 py-1 text-sm"
									>
										<option value="">N/A</option>
										{#each data.companies as company}
											<option value={company.uuid}>
												{company.name}
											</option>
										{/each}
									</select>

									<button
										class="text-xs text-[var(--color-primary)] underline"
										on:click={() => (showNewCompany = !showNewCompany)}
									>
										{showNewCompany ? 'Cancel new company' : '+ New Company'}
									</button>

									{#if showNewCompany}
										<input
											bind:value={newCompanyName}
											placeholder="Company name"
											class="w-full border rounded px-2 py-1 text-sm"
										/>
									{/if}

									<div class="flex gap-2">
										<button class="btn-primary" on:click={saveService} disabled={savingService}>
											{savingService ? '...' : 'Save'}
										</button>
										<button class="btn-cancel" on:click={cancelEditService}>Cancel</button>
									</div>
								</div>
							{:else}
								<div class="flex items-center gap-2 mt-1">
									<span class="info-value">{getCompanyForRole(role.role_name)?.company_name ?? 'N/A'}</span>
									<button class="btn-edit" on:click={() => startEditService(role.role_name)}>Edit</button>
								</div>
							{/if}
						</div>
					{/each}
				</div>

			<!-- TAB: Contracts -->
			{:else if activeTab === 'Contracts'}
				<div class="grid grid-cols-2 gap-6">
					<!-- Administration -->
					<div>
						<div class="flex items-center justify-between mb-2">
							<h2 class="section-title mb-0 pb-0 border-0">Administration</h2>
							{#if editingContractSection !== 'administration'}
								<button class="btn-edit" on:click={() => startEditContract('administration')}>Edit</button>
							{/if}
						</div>
						<FarmCard>
							{#if editingContractSection === 'administration'}
								<div class="space-y-3 text-sm">
									<div><label class="info-label block">SIRET</label><input bind:value={adminFields.siret_number} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
									<div><label class="info-label block">VAT Number</label><input bind:value={adminFields.vat_number} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
									<div><label class="info-label block">Account Number</label><input bind:value={adminFields.account_number} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
									<div><label class="info-label block">Legal Representative</label><input bind:value={adminFields.legal_representative} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
									<div><label class="info-label block">Head Office</label><input bind:value={adminFields.head_office_address} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
									<div><label class="info-label block">WM Subsidiary</label><input bind:value={adminFields.windmanager_subsidiary} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
									<div class="flex gap-2 pt-1">
										<button class="btn-primary" on:click={saveContract} disabled={savingContract}>{savingContract ? '...' : 'Save'}</button>
										<button class="btn-cancel" on:click={() => (editingContractSection = '')}>Cancel</button>
									</div>
								</div>
							{:else}
								<div class="space-y-2 text-sm">
									<div><span class="info-label">SIRET</span><div class="info-value">{fd?.administration?.siret_number ?? 'N/A'}</div></div>
									<div><span class="info-label">VAT Number</span><div class="info-value">{fd?.administration?.vat_number ?? 'N/A'}</div></div>
									<div><span class="info-label">Account Number</span><div class="info-value">{fd?.administration?.account_number ?? 'N/A'}</div></div>
									<div><span class="info-label">Legal Representative</span><div class="info-value">{fd?.administration?.legal_representative ?? 'N/A'}</div></div>
									<div><span class="info-label">Head Office</span><div class="info-value">{fd?.administration?.head_office_address ?? 'N/A'}</div></div>
									<div><span class="info-label">WM Subsidiary</span><div class="info-value">{fd?.administration?.windmanager_subsidiary ?? 'N/A'}</div></div>
								</div>
							{/if}
						</FarmCard>
					</div>

					<div class="space-y-6">
						<!-- O&M Contract -->
						<div>
							<div class="flex items-center justify-between mb-2">
								<h2 class="section-title mb-0 pb-0 border-0">O&M Contract</h2>
								{#if editingContractSection !== 'om-contract'}
									<button class="btn-edit" on:click={() => startEditContract('om-contract')}>Edit</button>
								{/if}
							</div>
							<FarmCard>
								{#if editingContractSection === 'om-contract'}
									<div class="space-y-3 text-sm">
										<div><label class="info-label block">Contract Type</label><input bind:value={omFields.service_contract_type} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
										<div><label class="info-label block">End Date</label><input type="date" bind:value={omFields.contract_end_date} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
										<div class="flex gap-2 pt-1">
											<button class="btn-primary" on:click={saveContract} disabled={savingContract}>{savingContract ? '...' : 'Save'}</button>
											<button class="btn-cancel" on:click={() => (editingContractSection = '')}>Cancel</button>
										</div>
									</div>
								{:else}
									<div class="space-y-2 text-sm">
										<div><span class="info-label">Contract Type</span><div class="info-value">{fd?.omContract?.service_contract_type ?? 'N/A'}</div></div>
										<div><span class="info-label">End Date</span><div class="info-value">{fd?.omContract?.contract_end_date ?? 'N/A'}</div></div>
									</div>
								{/if}
							</FarmCard>
						</div>

						<!-- TCMA Contract -->
						<div>
							<div class="flex items-center justify-between mb-2">
								<h2 class="section-title mb-0 pb-0 border-0">TCMA Contract</h2>
								{#if editingContractSection !== 'tcma-contract'}
									<button class="btn-edit" on:click={() => startEditContract('tcma-contract')}>Edit</button>
								{/if}
							</div>
							<FarmCard>
								{#if editingContractSection === 'tcma-contract'}
									<div class="space-y-3 text-sm">
										<div><label class="info-label block">Contract Type</label><input bind:value={tcmaFields.contract_type} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
										<div><label class="info-label block">Status</label><input bind:value={tcmaFields.tcma_status} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
										<div><label class="info-label block">Effective Date</label><input type="date" bind:value={tcmaFields.effective_date} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
										<div><label class="info-label block">End Date</label><input type="date" bind:value={tcmaFields.end_date} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
										<div class="flex gap-2 pt-1">
											<button class="btn-primary" on:click={saveContract} disabled={savingContract}>{savingContract ? '...' : 'Save'}</button>
											<button class="btn-cancel" on:click={() => (editingContractSection = '')}>Cancel</button>
										</div>
									</div>
								{:else}
									<div class="space-y-2 text-sm">
										<div><span class="info-label">Contract Type</span><div class="info-value">{fd?.tcmaContract?.contract_type ?? 'N/A'}</div></div>
										<div><span class="info-label">Status</span><div class="info-value">{fd?.tcmaContract?.tcma_status ?? 'N/A'}</div></div>
										<div><span class="info-label">Effective Date</span><div class="info-value">{fd?.tcmaContract?.effective_date ?? 'N/A'}</div></div>
										<div><span class="info-label">End Date</span><div class="info-value">{fd?.tcmaContract?.end_date ?? 'N/A'}</div></div>
									</div>
								{/if}
							</FarmCard>
						</div>

						<!-- Financial Guarantee -->
						<div>
							<div class="flex items-center justify-between mb-2">
								<h2 class="section-title mb-0 pb-0 border-0">Financial Guarantee</h2>
								{#if editingContractSection !== 'financial-guarantee'}
									<button class="btn-edit" on:click={() => startEditContract('financial-guarantee')}>Edit</button>
								{/if}
							</div>
							<FarmCard>
								{#if editingContractSection === 'financial-guarantee'}
									<div class="space-y-3 text-sm">
										<div><label class="info-label block">Amount (EUR)</label><input type="number" bind:value={finGuarFields.amount} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
										<div><label class="info-label block">Due Date</label><input type="date" bind:value={finGuarFields.due_date} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
										<div class="flex gap-2 pt-1">
											<button class="btn-primary" on:click={saveContract} disabled={savingContract}>{savingContract ? '...' : 'Save'}</button>
											<button class="btn-cancel" on:click={() => (editingContractSection = '')}>Cancel</button>
										</div>
									</div>
								{:else}
									<div class="space-y-2 text-sm">
										<div><span class="info-label">Amount</span><div class="info-value">{fd?.financialGuarantee?.amount != null ? `${fd.financialGuarantee.amount.toLocaleString()} EUR` : 'N/A'}</div></div>
										<div><span class="info-label">Due Date</span><div class="info-value">{fd?.financialGuarantee?.due_date ?? 'N/A'}</div></div>
									</div>
								{/if}
							</FarmCard>
						</div>

						<!-- Electrical Delegation -->
						<div>
							<div class="flex items-center justify-between mb-2">
								<h2 class="section-title mb-0 pb-0 border-0">Electrical Delegation</h2>
								{#if editingContractSection !== 'electrical-delegation'}
									<button class="btn-edit" on:click={() => startEditContract('electrical-delegation')}>Edit</button>
								{/if}
							</div>
							<FarmCard>
								{#if editingContractSection === 'electrical-delegation'}
									<div class="space-y-3 text-sm">
										<div class="flex items-center gap-2">
											<label class="info-label">In Place</label>
											<input type="checkbox" bind:checked={elecDelFields.in_place} class="rounded" />
										</div>
										<div><label class="info-label block">DREI Date</label><input type="date" bind:value={elecDelFields.drei_date} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
										<div class="flex gap-2 pt-1">
											<button class="btn-primary" on:click={saveContract} disabled={savingContract}>{savingContract ? '...' : 'Save'}</button>
											<button class="btn-cancel" on:click={() => (editingContractSection = '')}>Cancel</button>
										</div>
									</div>
								{:else}
									<div class="space-y-2 text-sm">
										<div><span class="info-label">In Place</span><div class="info-value">{fd?.electricalDelegation?.in_place ? 'Yes' : 'No'}</div></div>
										<div><span class="info-label">DREI Date</span><div class="info-value">{fd?.electricalDelegation?.drei_date ?? 'N/A'}</div></div>
									</div>
								{/if}
							</FarmCard>
						</div>

						<!-- Environmental Installation -->
						<div>
							<div class="flex items-center justify-between mb-2">
								<h2 class="section-title mb-0 pb-0 border-0">Environmental Installation</h2>
								{#if editingContractSection !== 'environmental-installation'}
									<button class="btn-edit" on:click={() => startEditContract('environmental-installation')}>Edit</button>
								{/if}
							</div>
							<FarmCard>
								{#if editingContractSection === 'environmental-installation'}
									<div class="space-y-3 text-sm">
										<div><label class="info-label block">AIP Number</label><input bind:value={envInstFields.aip_number} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
										<div><label class="info-label block">Prefecture</label><input bind:value={envInstFields.prefecture_name} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
										<div><label class="info-label block">DREAL Contact</label><input bind:value={envInstFields.duty_dreal_contact} class="w-full border rounded px-2 py-1 text-sm mt-1" /></div>
										<div class="flex gap-2 pt-1">
											<button class="btn-primary" on:click={saveContract} disabled={savingContract}>{savingContract ? '...' : 'Save'}</button>
											<button class="btn-cancel" on:click={() => (editingContractSection = '')}>Cancel</button>
										</div>
									</div>
								{:else}
									<div class="space-y-2 text-sm">
										<div><span class="info-label">AIP Number</span><div class="info-value">{fd?.environmentalInstallation?.aip_number ?? 'N/A'}</div></div>
										<div><span class="info-label">Prefecture</span><div class="info-value">{fd?.environmentalInstallation?.prefecture_name ?? 'N/A'}</div></div>
										<div><span class="info-label">DREAL Contact</span><div class="info-value">{fd?.environmentalInstallation?.duty_dreal_contact ?? 'N/A'}</div></div>
									</div>
								{/if}
							</FarmCard>
						</div>
					</div>
				</div>

			<!-- TAB: Location -->
			{:else if activeTab === 'Location'}
				<h2 class="section-title">Location</h2>

				{#if editingLocation}
					<div class="grid grid-cols-2 gap-6">
						<div class="space-y-3">
							<div class="info-card">
								<label class="info-label block">Country</label>
								<input bind:value={locFields.country} class="w-full border rounded px-2 py-1 text-sm mt-1" />
							</div>
							<div class="info-card">
								<label class="info-label block">Region</label>
								<input bind:value={locFields.region} class="w-full border rounded px-2 py-1 text-sm mt-1" />
							</div>
							<div class="info-card">
								<label class="info-label block">Department</label>
								<input bind:value={locFields.department} class="w-full border rounded px-2 py-1 text-sm mt-1" />
							</div>
							<div class="info-card">
								<label class="info-label block">Municipality</label>
								<input bind:value={locFields.municipality} class="w-full border rounded px-2 py-1 text-sm mt-1" />
							</div>
						</div>
						<div class="space-y-3">
							<div class="info-card">
								<label class="info-label block">Map Reference</label>
								<input bind:value={locFields.map_reference} class="w-full border rounded px-2 py-1 text-sm mt-1" />
							</div>
							<div class="info-card">
								<label class="info-label block">Arras Round Trip (km)</label>
								<input type="number" bind:value={locFields.arras_round_trip_distance_km} class="w-full border rounded px-2 py-1 text-sm mt-1" />
							</div>
							<div class="info-card">
								<label class="info-label block">Vertou Round Trip (h)</label>
								<input type="number" bind:value={locFields.vertou_round_trip_duration_h} class="w-full border rounded px-2 py-1 text-sm mt-1" />
							</div>
							<div class="info-card">
								<label class="info-label block">Arras Toll (EUR)</label>
								<input type="number" bind:value={locFields.arras_toll_eur} class="w-full border rounded px-2 py-1 text-sm mt-1" />
							</div>
							<div class="info-card">
								<label class="info-label block">Nantes Toll (EUR)</label>
								<input type="number" bind:value={locFields.nantes_toll_eur} class="w-full border rounded px-2 py-1 text-sm mt-1" />
							</div>
						</div>
					</div>
					<div class="flex gap-2 mt-4">
						<button class="btn-primary" on:click={saveLocation} disabled={savingLocation}>
							{savingLocation ? 'Saving...' : 'Save'}
						</button>
						<button class="btn-cancel" on:click={() => (editingLocation = false)}>Cancel</button>
					</div>
				{:else}
					<button class="btn-primary mb-4" on:click={startEditLocation}>Edit Location</button>

					<div class="grid grid-cols-2 gap-6">
						<div>
							<h3 class="section-title text-sm">Geographic Location</h3>
							<FarmCard>
								<div class="space-y-2 text-sm">
									<div><span class="info-label">Country</span><div class="info-value">{fd?.location?.country ?? 'N/A'}</div></div>
									<div><span class="info-label">Region</span><div class="info-value">{fd?.location?.region ?? 'N/A'}</div></div>
									<div><span class="info-label">Department</span><div class="info-value">{fd?.location?.department ?? 'N/A'}</div></div>
									<div><span class="info-label">Municipality</span><div class="info-value">{fd?.location?.municipality ?? 'N/A'}</div></div>
								</div>
							</FarmCard>
						</div>
						<div>
							<h3 class="section-title text-sm">Distances & Travel</h3>
							<FarmCard>
								<div class="space-y-2 text-sm">
									<div><span class="info-label">Arras Distance</span><div class="info-value">{fd?.location?.arras_round_trip_distance_km ?? 'N/A'} km</div></div>
									<div><span class="info-label">Vertou Duration</span><div class="info-value">{fd?.location?.vertou_round_trip_duration_h ?? 'N/A'} h</div></div>
									<div><span class="info-label">Arras Toll</span><div class="info-value">{fd?.location?.arras_toll_eur ?? 'N/A'} EUR</div></div>
									<div><span class="info-label">Nantes Toll</span><div class="info-value">{fd?.location?.nantes_toll_eur ?? 'N/A'} EUR</div></div>
									<div><span class="info-label">Map Reference</span><div class="info-value">{fd?.location?.map_reference ?? 'N/A'}</div></div>
								</div>
							</FarmCard>
						</div>
					</div>
				{/if}
			{/if}
		{:else}
			<div class="text-center text-gray-400 py-16">
				<p class="text-lg">Select a farm from the sidebar</p>
			</div>
		{/if}
	</main>
</div>
