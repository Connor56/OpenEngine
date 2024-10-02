<script>
	import { onMount } from 'svelte';
	import { page } from '$app/stores';

	let query = '';
	let results = ['hi'];

	$: query = $page.url.searchParams.get('query') || '';

	onMount(async () => {
		// Get query parameter from the URL
		console.log(query);

		if (query) {
			await fetchResults();
		}
	});

	async function fetchResults() {
		try {
			const response = await fetch(
				`http://localhost:8000/api/search?query=${encodeURIComponent(query)}`
			);
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
</script>

<div class="search-container">
	<h1>Search Results</h1>
	<input type="text" bind:value={query} placeholder="Enter a search query" />
</div>

<div class="results-container">
	{#if results.length > 0}
		{#each results as result}
			<div class="result-item">
				<a class="result-title" href={result.url} target="_blank">{result.title}</a>
				<div class="result-url">{result.url}</div>
				<div class="result-snippet">{result.snippet}</div>
			</div>
		{/each}
	{:else}
		<p>No results found for "{query}".</p>
	{/if}
</div>

<style>
	/* Your styles here */
	.results-container {
		margin: 50px auto;
		width: 60%;
	}

	.result-item {
		margin-bottom: 20px;
	}

	.result-title {
		font-size: 18px;
		color: #1a0dab;
		text-decoration: none;
	}

	.result-url {
		font-size: 14px;
		color: #006621;
	}

	.result-snippet {
		font-size: 14px;
		color: #545454;
	}
</style>
