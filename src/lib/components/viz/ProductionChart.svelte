<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { Chart, registerables } from 'chart.js';

	Chart.register(...registerables);

	export let farmUuid: string;
	export let hours: number = 24;

	let canvas: HTMLCanvasElement;
	let chart: Chart | null = null;
	let loading = true;
	let noData = false;

	async function loadData() {
		loading = true;
		noData = false;

		try {
			const res = await fetch(`/api/farms/${farmUuid}/production?hours=${hours}`);
			if (!res.ok) { noData = true; loading = false; return; }

			const raw: { pu_id: string; timestamp: string; active_power_avg_kw: number | null; wind_speed_avg_ms: number | null }[] = await res.json();

			if (raw.length === 0) { noData = true; loading = false; return; }

			// Aggregate by timestamp: sum power, average wind speed
			const byTime = new Map<string, { power: number; wind: number; count: number }>();
			for (const r of raw) {
				const key = r.timestamp;
				const existing = byTime.get(key) ?? { power: 0, wind: 0, count: 0 };
				existing.power += r.active_power_avg_kw ?? 0;
				existing.wind += r.wind_speed_avg_ms ?? 0;
				existing.count += 1;
				byTime.set(key, existing);
			}

			const sorted = [...byTime.entries()].sort((a, b) => a[0].localeCompare(b[0]));
			const labels = sorted.map(([ts]) => {
				const d = new Date(ts);
				return d.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
			});
			const powerData = sorted.map(([, v]) => Math.round(v.power));
			const windData = sorted.map(([, v]) => v.count > 0 ? Math.round(v.wind / v.count * 10) / 10 : 0);

			if (chart) chart.destroy();

			chart = new Chart(canvas, {
				type: 'line',
				data: {
					labels,
					datasets: [
						{
							label: 'Puissance (kW)',
							data: powerData,
							borderColor: '#1565c0',
							backgroundColor: 'rgba(21, 101, 192, 0.1)',
							fill: true,
							tension: 0.3,
							pointRadius: 0,
							yAxisID: 'y'
						},
						{
							label: 'Vent (m/s)',
							data: windData,
							borderColor: '#66bb6a',
							backgroundColor: 'rgba(102, 187, 106, 0.1)',
							fill: false,
							tension: 0.3,
							pointRadius: 0,
							yAxisID: 'y1'
						}
					]
				},
				options: {
					responsive: true,
					maintainAspectRatio: false,
					interaction: { mode: 'index', intersect: false },
					plugins: {
						legend: { position: 'top' },
						tooltip: {
							callbacks: {
								title: (items) => items[0]?.label ?? ''
							}
						}
					},
					scales: {
						x: {
							ticks: {
								maxTicksLimit: 12,
								font: { size: 10 }
							},
							grid: { display: false }
						},
						y: {
							type: 'linear',
							position: 'left',
							title: { display: true, text: 'kW' },
							beginAtZero: true
						},
						y1: {
							type: 'linear',
							position: 'right',
							title: { display: true, text: 'm/s' },
							beginAtZero: true,
							grid: { drawOnChartArea: false }
						}
					}
				}
			});
		} catch {
			noData = true;
		}

		loading = false;
	}

	onMount(() => loadData());
	onDestroy(() => { if (chart) chart.destroy(); });

	// Reload when farm changes
	$: if (farmUuid && canvas) loadData();
</script>

<div class="bg-white rounded-lg shadow-sm p-4">
	<div class="flex items-center justify-between mb-3">
		<h3 class="font-semibold text-sm text-gray-700">Production temps réel ({hours}h)</h3>
		<div class="flex gap-1">
			<button
				class="text-xs px-2 py-1 rounded {hours === 6 ? 'bg-[#1565c0] text-white' : 'bg-gray-100 text-gray-600'}"
				on:click={() => { hours = 6; loadData(); }}
			>6h</button>
			<button
				class="text-xs px-2 py-1 rounded {hours === 24 ? 'bg-[#1565c0] text-white' : 'bg-gray-100 text-gray-600'}"
				on:click={() => { hours = 24; loadData(); }}
			>24h</button>
			<button
				class="text-xs px-2 py-1 rounded {hours === 72 ? 'bg-[#1565c0] text-white' : 'bg-gray-100 text-gray-600'}"
				on:click={() => { hours = 72; loadData(); }}
			>3j</button>
			<button
				class="text-xs px-2 py-1 rounded {hours === 168 ? 'bg-[#1565c0] text-white' : 'bg-gray-100 text-gray-600'}"
				on:click={() => { hours = 168; loadData(); }}
			>7j</button>
		</div>
	</div>

	{#if loading}
		<div class="h-64 flex items-center justify-center text-gray-400 text-sm">
			Chargement des données de production...
		</div>
	{:else if noData}
		<div class="h-64 flex items-center justify-center text-gray-400 text-sm">
			Aucune donnée de production disponible pour ce parc
		</div>
	{/if}

	<div class="h-64" class:hidden={loading || noData}>
		<canvas bind:this={canvas}></canvas>
	</div>
</div>
