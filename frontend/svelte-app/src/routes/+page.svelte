<script>
<script lang="ts">
	let query = '';

	function handleSearch() {
		// Navigate to the results page with the query as a URL parameter
		window.location.href = `/results?query=${encodeURIComponent(query)}`;
	}

	function handleKeyPress(event) {
		if (event.key === 'Enter') {
			handleSearch();
		}
	}
</script>

<div class="search-bar">
	<input
		type="text"
		class="search-input"
		bind:value={query}
		on:keypress={handleKeyPress}
		placeholder="Search..."
	/>
</div>

<style>
	/* Your styles here */
	.search-bar {
		display: flex;
		justify-content: center;
		height: 100vh;
		align-items: center;
	}

	.search-input {
		width: 550px;
		height: 24px;
		padding: 10px 20px;
		font-size: 18px;
		border-radius: 100px;
		border: 1px solid #dfe1e5;
	}

	.search-input:focus {
		outline: none;
		border: 1px solid rgb(255, 255, 255);
		box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
	}

	.search-input:hover {
		outline: none;
		border: 1px solid #ffffff;
		box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
	}

	:global(body) {
		background-color: #ffffff;
		/* background-color: rgb(149, 141, 236); */
		/* background-image: linear-gradient(rgb(149, 141, 236), #cd2020); */
		/* background-image: linear-gradient(rgb(149, 141, 236), #ffffff); */
		/* background-image: linear-gradient(rgb(149, 141, 236), #000000); */
	}
</style>
