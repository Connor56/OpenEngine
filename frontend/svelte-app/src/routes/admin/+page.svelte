<script lang="ts">
	import AdminTopNav from '$lib/components/AdminTopNav.svelte';
	import UrlPanel from '$lib/components/UrlPanel.svelte';
	import Button from '$lib/components/Button.svelte';
	import type { Url } from '$lib/types';
	import { onMount } from 'svelte';

	let seedUrls: Url[] = [
		{
			url: 'https://github.com',
			faviconLocation: 'github.webp'
		}
	];
	let newUrl = '';

	let adminLocation = 'seed-urls';

	function handleNav(event: Event) {
		const target = event.target as HTMLElement;
		adminLocation = target.id;
	}

	function handleDelete(index: number) {
		let removedUrl = seedUrls[index];
		seedUrls = seedUrls.filter((_, i) => i !== index);
	}

	function handleSelect(index: number) {
		let selectedUrl = seedUrls[index];
		alert(selectedUrl.url);
	}

	let API_URL: string;

	onMount(async () => {
		let response = await fetch('/env.json');
		const env = await response.json();

		// Get the API_URL
		API_URL = env.API_URL;

		response = await fetch(`${API_URL}/get-seed-urls`, {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
				Authorization: `Bearer askldjklasdjf` // Add the Authorization header
			}
		});

		seedUrls = await response.json();
	});
</script>

<container>
	<AdminTopNav {handleNav} />
	<div class="admin-container">
		{#if adminLocation === 'seed-urls'}
			<div class="seed-url-grid">
				<div class="seed-url-pane standard-pane">
					<h2>Seed Urls</h2>
					<UrlPanel {seedUrls} {handleDelete} {handleSelect} />
				</div>
				<div class="url-meta standard-pane">
					<h2>Url Metadata</h2>
				</div>
				<div class="url-investigation standard-pane">
					<h2>Investigate Urls</h2>
				</div>
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
		grid-row: 1 / span 3; /* Span 3 rows */
	}

	.url-investigation {
		grid-column: 2; /* Move to the second column */
		grid-row: 4 / span 2; /* Span 1 row */
	}

	.standard-pane {
		background-color: white;
		border-radius: 30px;
		padding: 20px;
		box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
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
