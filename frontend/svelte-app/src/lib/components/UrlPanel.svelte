<script lang="ts">
	import type { Url } from '$lib/types';
	import UrlCard from './UrlCard.svelte';

	export let seedUrls: Url[];
	export let handleDelete: (index: number) => void;
	export let handleSelect: (index: number) => void;
</script>

<div class="url-panel">
	{#each seedUrls as url, index}
		<UrlCard {url} on:delete={() => handleDelete(index)} on:select={() => handleSelect(index)} />
	{/each}
</div>

<style>
	.url-panel {
		margin-top: 30px;
	}

	}

	}

	}

	}
</style>
