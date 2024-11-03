<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import SearchBar from '$lib/components/SearchBar.svelte';
	import type { Result } from '$lib/types';
	import ResultCard from '$lib/components/ResultCard.svelte';

	let query: string | null = '';
	let results: Result[] = [];

	let API_URL: string = '';

	onMount(async () => {
		// Get query parameter from the URL
		query = $page.url.searchParams.get('query');

		// Load the environment variables
		let response = await fetch('/env.json');
		const env = await response.json();

		// Get the API_URL
		API_URL = env.API_URL;

		console.log(API_URL);

		if (query) {
			await fetchResults();
		}
	});

	async function fetchResults() {
		try {
			const response = await fetch(`${API_URL}/search?query=${encodeURIComponent(query)}`);
			if (response.ok) {
				const data = await response.json();
				results = data.results;
			} else {
				console.error('Error fetching results');
			}
		} catch (error) {
			console.error('Error:', error);
		}
	}

	const handleKeyPress = (event: KeyboardEvent) => {
		if (event.key === 'Enter') {
			alert('you pressed enter');
		}
	};
</script>

<div class="top-bar horizontal-alignment">
	<SearchBar {handleKeyPress} {query} />
</div>
<hr />

<div class="results-container horizontal-alignment">
	{#if results.length > 0}
		{#each results as result}
			<div class="result-item">
				<ResultCard {result} />
			</div>
		{/each}
	{:else}
		<p>No results found for "{query}".</p>
	{/if}
</div>

<style>
	.top-bar {
		margin-top: 30px;
		margin-bottom: 56px;
	}

	.horizontal-alignment {
		margin-left: 150px;
		max-width: 600px;
		min-width: 600px;
	}

	@media (max-width: 1000px) {
		.horizontal-alignment {
			margin-left: clamp(20px, 45% - 300px, 15%);
		}
	}

	hr {
		width: 100%; /* Makes the rule span the entire width of the page */
		border: none; /* Removes the default border */
		border-top: 1px solid #dfe1e5; /* Adds a custom border (you can adjust thickness and color) */
		margin: 0; /* Removes any default margin */
	}

	.results-container {
		margin-top: 30px;
	}

	:global(body) {
		background-color: #ffffff;
		margin: 0;
	}
</style>
