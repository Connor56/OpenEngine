<script lang="ts">
	import SearchBar from '$lib/components/SearchBar.svelte';

	function handleSearch(query: string) {
		// Navigate to the results page with the query as a URL parameter
		console.log(query);
		window.location.href = `/results?query=${encodeURIComponent(query)}`;
	}

	const handleKeyPress = (event: KeyboardEvent) => {
		if (event.key === 'Enter') {
			handleSearch(event?.target?.value);
		}
	};
</script>

<div class="search-container">
	<SearchBar {handleKeyPress} />
</div>

<style>
	.search-container {
		display: flex;
		justify-content: center;
		height: 100vh;
		align-items: center;
	}

	:global(body) {
		background-color: #ffffff;
		/* background-color: rgb(149, 141, 236); */
		/* background-image: linear-gradient(rgb(149, 141, 236), #cd2020); */
		/* background-image: linear-gradient(rgb(149, 141, 236), #ffffff); */
		/* background-image: linear-gradient(rgb(149, 141, 236), #000000); */
	}
</style>
