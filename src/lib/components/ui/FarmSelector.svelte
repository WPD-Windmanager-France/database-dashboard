<script lang="ts">
	import type { FarmWithType } from '$lib/types/farm';

	export let farms: FarmWithType[];
	export let selectedUuid: string;
</script>

<div class="farm-list-scroll space-y-1">
	{#each farms as farm (farm.uuid)}
		<a
			href="/data?farm={farm.uuid}"
			class="block rounded-lg px-3 py-2 transition-colors {farm.uuid === selectedUuid
				? 'bg-[var(--color-primary)] text-white shadow'
				: 'bg-white hover:bg-gray-100 text-gray-700'}"
		>
			<div class="font-semibold text-sm">{farm.project}</div>
			<div class="text-xs opacity-75">{farm.code} &middot; {farm.spv}</div>
		</a>
	{/each}
</div>
