<script lang="ts">
	import type { Url } from '$lib/types';
	import UrlCard from './UrlCard.svelte';

	export let seedUrls: Url[];
</script>

<div class="url-panel">
	{#each seedUrls as url}
		<UrlCard {url} />
	{/each}
</div>

<style>
	.url-panel {
		margin-top: 30px;
	}

	.url-item {
		margin-bottom: 20px;
	}

	.url-title {
		font-size: 18px;
		color: #368aff;
		text-decoration: none;
	}

	h3 {
		font-weight: 400;
		margin-top: 8px;
		margin-bottom: 8px;
	}

	.url-title:hover {
		text-decoration: underline;
	}

	.url-title:visited {
		color: #b45eff;
	}

	.url-url {
		font-size: 14px;
		color: #191919;
		margin-top: 0;
	}
</style>
