<script lang="ts">
	export let handleKeyPress: (event: KeyboardEvent) => void;

	export let query: string = '';
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
	.search-input {
		width: 550px;
		height: 24px;
		padding: 10px 20px;
		font-size: 18px;
		font-family: 'Roboto', sans-serif;
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
</style>
