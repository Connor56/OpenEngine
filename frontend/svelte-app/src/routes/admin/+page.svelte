<script lang="ts">
	import AdminTopNav from '$lib/components/AdminTopNav.svelte';

	let seedUrls = ['https://an_url.com'];
	let newUrl = '';
</script>

<AdminTopNav />
<div class="admin-container"></div>

<style>
	/* Your styles here */
	.admin-container {
		margin: 50px auto;
		width: 60%;
	}

	.url-list {
		list-style: none;
		padding: 0;
	}

	.url-item {
		display: flex;
		justify-content: space-between;
		margin-bottom: 10px;
	}

	.add-url {
		display: flex;
		margin-bottom: 20px;
	}

	.add-url input {
		flex: 1;
		margin-right: 10px;
	}

	:global(body) {
		background-color: #ffffff;
		margin: 0;
	}
</style>
