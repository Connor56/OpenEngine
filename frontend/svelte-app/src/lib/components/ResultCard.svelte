<script lang="ts">
	import type { Result } from '$lib/types';

	export let result: Result;
</script>

<div class="result-card">
	<div class="select-on-hover">
		<a class="result-card-link" href={result.url}>
			<div class="result-card-header">
				<img class="result-card-favicon" src={result.faviconLocation} alt="favicon" />
				<div class="result-card-overview">
					<div class="overview-site-name">{result.siteName}</div>
					<div class="overview-url">{result.url}</div>
				</div>
			</div>
		</a>
		<a class="result-title" href={result.url}><h3>{result.title}</h3></a>
	</div>
	<p class="result-card-snippet">
		<span class="snippet-date">{result.published} — </span>{result.snippet}
	</p>
</div>

<style>
	.result-card {
		margin-bottom: 40px;
	}

	.result-card-link {
		text-decoration: none;
	}

	.select-on-hover:hover {
		cursor: pointer;
	}

	.result-card-header {
		display: flex;
		flex-direction: row;
	}

	.result-card-favicon {
		width: 34px;
		height: 34px;
		margin-right: 10px;
	}

	.overview-site-name {
		font-size: 20px;
		color: #545454;
	}

	.overview-url {
		font-size: 16px;
		color: #7f7f7f;
	}

	.result-card-overview {
		display: flex;
		flex-direction: column;
	}

	.result-title {
		font-size: 18px;
		color: #368aff;
		text-decoration: none;
	}

	h3 {
		font-weight: 400;
		margin-top: 8px;
		margin-bottom: 8px;
	}

	.result-title:hover {
		text-decoration: underline;
	}

	.result-title:visited {
		color: #b45eff;
	}

	.result-card-snippet {
		font-size: 14px;
		/* color: #545454; */
		color: #191919;
		margin-top: 0;
	}

	.snippet-date {
		color: #565656;
	}
</style>
