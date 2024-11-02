<script lang="ts">
	import AdminTopNav from '$lib/components/AdminTopNav.svelte';
	import UrlPanel from '$lib/components/UrlPanel.svelte';
	import SeedCard from '$lib/components/SeedCard.svelte';
	import Button from '$lib/components/Button.svelte';
	import SeedEditModal from '$lib/components/SeedEditModal.svelte';
	import type { Url } from '$lib/types';
	import { onMount } from 'svelte';

	let coreResources: Url[];

	let adminLocation = 'seed-urls';
	let selectedResource: Url = { url: '', faviconLocation: '', seeds: [] };
	let loading = true;

	function handleNav(event: Event) {
		const target = event.target as HTMLElement;
		adminLocation = target.id;
	}

	function handleSelect(index: number) {
		let selectedUrl = coreResources[index];
		selectedResource = selectedUrl;
		selectedResource.seeds = ['/some/seed/url', '/another/seed/url'];
	}

	let API_URL: string;

	onMount(async () => {
		let response = await fetch('/env.json');
		const env = await response.json();

		// Get the API_URL
		API_URL = env.API_URL;

		// Reload the urls
		await reloadUrls();

		loading = false;
	});

	/**
	 * Loads the core urls from the API.
	 */
	async function reloadUrls() {
		const response = await fetch(`${API_URL}/get-seed-urls`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer askldjklasdjf` // Add the Authorization header
			}
		});

		coreResources = await response.json();
	}
</script>

<container>
	<AdminTopNav {handleNav} />
	<div class="admin-container">
		{#if adminLocation === 'seed-urls'}
			<div class="seed-url-grid">
				<div class="seed-url-pane standard-pane">
					<h2>Core Resources</h2>
					{#if !loading}
						<UrlPanel
							{coreResources}
							{handleSelect}
							selectedResource={selectedResource.url}
							on:close={reloadUrls}
						/>
					{/if}
				</div>
				<div class="url-meta standard-pane">
					<h2>Resource Management</h2>
					<h3>Seeds</h3>
					<div class="resource-seeds">
						{#each selectedResource.seeds as seed}
							<SeedCard
								{seed}
								url={selectedResource.url}
								on:delete={() => handleSeedDelete(seed)}
								on:edit={() => {
									seedModal = true;
									currentSeed = seed;
									seedEdit = true;
									console.log(currentSeed);
								}}
							></SeedCard>
						{/each}
						{#if selectedResource.url !== ''}
							<div class="button-container">
								<button on:click={handleSeedAdd}>
									<svg class="url-add" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
										<path
											d="M24 16V32M16 24H32M44 24C44 35.0457 35.0457 44 24 44C12.9543 44 4 35.0457 4 24C4 12.9543 12.9543 4 24 4C35.0457 4 44 12.9543 44 24Z"
											stroke-width="4"
											stroke-linecap="round"
											stroke-linejoin="round"
										/>
									</svg>
								</button>
							</div>
						{/if}
					</div>
				</div>
				{#if seedModal}
					<SeedEditModal
						url={selectedResource}
						seed={currentSeed}
						edit={seedEdit}
						on:close={seedModalClose}
					/>
				{/if}
			</div>
		{:else if adminLocation === 'crawl'}
			<div class="crawl-grid">
				<div class="crawl-options-pane standard-pane">
					<h2>Options</h2>
				</div>
				<div class="crawl-tracking-pane standard-pane">
					<h2>Tracker</h2>
				</div>
				<div class="crawl-control-pane standard-pane">
					<h2>Controls</h2>
					<Button
						label="Start Crawl"
						color="#28b828"
						hoverBackgroundColor="#28b828"
						handleClick={() => alert('start crawl')}
					/>
					<Button
						label="Stop Crawl"
						color="#b82828"
						hoverBackgroundColor="#b82828"
						handleClick={() => alert('stop crawl')}
					/>
					<Button
						label="Pause Crawl"
						color="#d5890f"
						hoverBackgroundColor="#d5890f"
						handleClick={() => alert('pause crawl')}
					/>
				</div>
				<div class=""></div>
			</div>
		{:else if adminLocation === 'metrics'}
			<div>Metrics</div>
		{:else if adminLocation === 'settings'}
			<div>Settings</div>
		{/if}
	</div>
</container>

<style>
	h2 {
		margin-top: 0px;
	}

	.admin-container {
		margin: 30px 40px;
		display: flex;
		height: 100%;
		margin-bottom: 0px;
	}

	.seed-url-grid {
		display: grid;
		grid-template-columns: 3fr 5fr;
		grid-template-rows: repeat(5, 1fr); /* Three rows, each taking 1/3 of the height */
		grid-gap: 40px; /* Spacing between items */
		padding: 20px;
		flex-grow: 1;
	}

	.seed-url-pane {
		grid-column: 1; /* Stay in the first column */
		grid-row: 1 / span 5; /* Span 3 rows */
	}

	.url-meta {
		grid-column: 2; /* Move to the second column */
		grid-row: 1 / span 5; /* Span 3 rows */
	}

	.url-investigation {
		grid-column: 2; /* Move to the second column */
		grid-row: 4 / span 2; /* Span 1 row */
	}

	.resource-seed {
		display: flex;
		background-color: #e4e4e4;
		border-radius: 0.5rem;
		padding: 0.5rem;
		margin: 0.5rem;
	}

	.standard-pane {
		background-color: white;
		border-radius: 30px;
		padding: 20px;
		box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
	}

	button {
		all: unset;
		cursor: pointer;
	}

	.button-container {
		display: flex;
		justify-content: center;
		margin-top: 40px;
	}

	.url-add {
		fill: none;
		width: 40px;
		height: 40px;
		stroke: #757575;
	}

	.url-add:hover {
		stroke: #368aff;
	}

	container {
		display: flex;
		flex-direction: column;
		height: 100vh;
	}

	.crawl-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		grid-template-rows: repeat(1, 1fr);
		grid-gap: 40px;
		padding: 20px;
		flex-grow: 1;
	}

	.crawl-options-pane {
		grid-column: 1;
		grid-row: 1 / span 1;
	}

	.crawl-tracking-pane {
		grid-column: 2 / span 2;
		grid-row: 1 / span 1;
	}

	.craw-control-pane {
		grid-column: 5;
		grid-row: 1 / span 1;
	}

	.admin-container {
		margin: 30px 40px;
		display: flex;
		height: 100%;
		margin-bottom: 0px;
	}

	:global(body) {
		background-color: #ffffff;
		margin: 0;
	}
</style>
