<script lang="ts">
	import AdminTopNav from '$lib/components/AdminTopNav.svelte';
	import UrlPanel from '$lib/components/UrlPanel.svelte';
	import type { Url } from '$lib/types';

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
</script>

<container>
	<AdminTopNav {handleNav} />
	{#if adminLocation === 'seed-urls'}
		<div class="admin-container">
			<div class="seed-url-grid">
				<div class="seed-url-pane standard-pane">
					<h2>Seed Urls</h2>
					<UrlPanel {seedUrls} />
				</div>
				<div class="url-meta standard-pane">
					<h2>Url Metadata</h2>
				</div>
				<div class="url-investigation standard-pane">
					<h2>Investigate Urls</h2>
				</div>
				<div class=""></div>
			</div>
		</div>
	{:else if adminLocation === 'crawl'}
		<div>Crawl</div>
	{:else if adminLocation === 'metrics'}
		<div>Metrics</div>
	{:else if adminLocation === 'settings'}
		<div>Settings</div>
	{/if}
</container>

<style>
	h2 {
		margin-top: 0px;
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
		border: solid 1px #ccc;
		border-radius: 30px;
		padding: 20px;
		box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
	}

	container {
		display: flex;
		flex-direction: column;
		height: 100vh;
	}

	/* Your styles here */
	.admin-container {
		margin: 30px 40px;
		display: flex;
		height: 100%;
		margin-bottom: 0px;
	}

	.url-list {
		list-style: none;
		padding: 0;
	}

	.url-item {
		display: flex;
		justify-content: space-between;
		margin-bottom: 10px;
	}

	.add-url {
		display: flex;
		margin-bottom: 20px;
	}

	.add-url input {
		flex: 1;
		margin-right: 10px;
	}

	:global(body) {
		background-color: #ffffff;
		margin: 0;
	}
</style>
