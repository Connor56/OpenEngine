<script lang="ts">
	import type { Link } from '$lib/types';

	export let links: Link[];
</script>

<div class="link-panel">
	{#each links as link}
		<div class="link-item">
			<a class="link-title" href={link.url}>{link.title}</a>
			<div class="link-url">{link.url}</div>
		</div>
	{/each}
</div>

<style>
	.link-panel {
		margin-top: 30px;
	}

	.link-item {
		margin-bottom: 20px;
	}

	.link-title {
		font-size: 18px;
		color: #368aff;
		text-decoration: none;
	}

	h3 {
		font-weight: 400;
		margin-top: 8px;
		margin-bottom: 8px;
	}

	.link-title:hover {
		text-decoration: underline;
	}

	.link-title:visited {
		color: #b45eff;
	}

	.link-url {
		font-size: 14px;
		color: #191919;
		margin-top: 0;
	}
</style>
