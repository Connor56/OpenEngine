<script lang="ts">
	import type { Url } from '$lib/types';
	import UrlCard from './UrlCard.svelte';

	export let seedUrls: Url[];
	export let handleDelete: (index: number) => void;
	export let handleAdd: () => void;
	export let handleSelect: (index: number) => void;
</script>

<div class="url-panel">
	{#each seedUrls as url, index}
		<UrlCard {url} on:delete={() => handleDelete(index)} on:select={() => handleSelect(index)} />
	{/each}
	<div class="button-container">
		<button on:click={handleAdd}>
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
</div>

<style>
	.url-panel {
		margin-top: 30px;
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

	button {
		all: unset;
		cursor: pointer;
	}

	.button-container {
		display: flex;
		justify-content: center;
		margin-top: 40px;
	}
</style>
