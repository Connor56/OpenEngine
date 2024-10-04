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

	}

	}

	}

	}
</style>
