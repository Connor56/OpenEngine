<script lang="ts">
	import { page } from '$app/stores';

	export let handleNav: () => void;
</script>

<div class="top-nav-container">
	<h2>OpenEngine</h2>
	<div class="admin-top-nav top-bar horizontal-alignment">
		<div class="admin-nav-container">
			<div class="admin-nav-item">
				<a id="seed-urls" on:click={handleNav}>Seed Urls</a>
			</div>
			<div class="admin-nav-item">
				<a id="crawl" on:click={handleNav}>Crawl</a>
			</div>
			<div class="admin-nav-item">
				<a id="metrics" on:click={handleNav}>Metrics</a>
			</div>
			<div class="admin-nav-item">
				<a id="settings" on:click={handleNav}>Settings</a>
			</div>
		</div>
	</div>
</div>
<hr />

<style>
	h2 {
		margin-left: 20px;
		margin-top: 0px;
		margin-bottom: 0px;
		margin-right: 0px;
		display: flex;
		align-items: center;
	}

	.top-bar {
		margin-top: 20px;
		margin-bottom: 20px;
		border-radius: 10px;
	}

	.horizontal-alignment {
		margin-left: 150px;
		max-width: 600px;
		min-width: 600px;
	}

	@media (max-width: 1000px) {
		.horizontal-alignment {
			margin-left: clamp(20px, 45% - 300px, 15%);
			width: 100%;
			min-width: 450px;
			margin-right: 20px;
		}
	}

	@media (max-width: 710px) {
		h2 {
			display: none;
		}
	}

	hr {
		width: 100%; /* Makes the rule span the entire width of the page */
		border: none; /* Removes the default border */
		border-top: 1px solid #dfe1e5; /* Adds a custom border (you can adjust thickness and color) */
		margin: 0; /* Removes any default margin */
	}

	.admin-top-nav {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20px;
		background-color: #ffffff;
		box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
	}

	.top-nav-container {
		display: flex;
		flex-direction: row;
	}

	.admin-nav-container {
		display: flex;
		align-items: center;
	}

	.admin-nav-item {
		margin-right: 20px;
	}

	.admin-nav-item:hover {
		cursor: pointer;
	}

	.admin-nav-item a {
		text-decoration: none;
		color: #545454;
	}

	.admin-nav-item a:hover {
		text-decoration: underline;
	}

	.active {
		color: #1a0dab;
	}
</style>
