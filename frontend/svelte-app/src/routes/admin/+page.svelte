<script>
	import { onMount } from 'svelte';

	let seedUrls = ['https://an_url.com'];
	let newUrl = '';

	onMount(async () => {
		await fetchSeedUrls();
	});

	async function fetchSeedUrls() {
		try {
			const response = await fetch('http://localhost:8000/api/admin/seed-urls');
			if (response.ok) {
				const data = await response.json();
				seedUrls = data.urls;
			} else {
				console.error('Error fetching seed URLs');
			}
		} catch (error) {
			console.error('Error:', error);
		}
	}

	async function addUrl() {
		if (newUrl.trim()) {
			try {
				const response = await fetch('http://localhost:8000/api/admin/seed-urls', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify({ url: newUrl.trim() })
				});
				if (response.ok) {
					seedUrls.push(newUrl.trim());
					newUrl = '';
				} else {
					console.error('Error adding URL');
				}
			} catch (error) {
				console.error('Error:', error);
			}
		}
	}

	async function deleteUrl(urlToDelete) {
		try {
			const response = await fetch(`http://localhost:8000/api/admin/seed-urls`, {
				method: 'DELETE',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ url: urlToDelete })
			});
			if (response.ok) {
				seedUrls = seedUrls.filter((url) => url !== urlToDelete);
			} else {
				console.error('Error deleting URL');
			}
		} catch (error) {
			console.error('Error:', error);
		}
	}

	async function startCrawl() {
		try {
			const response = await fetch('http://localhost:8000/api/admin/start-crawl', {
				method: 'POST'
			});
			if (response.ok) {
				alert('Crawl started successfully!');
			} else {
				console.error('Error starting crawl');
			}
		} catch (error) {
			console.error('Error:', error);
		}
	}
</script>

<div class="admin-container">
	<h2>Admin Page</h2>

	<div class="add-url">
		<input type="text" bind:value={newUrl} placeholder="Enter seed URL" />
		<button on:click={addUrl}>Add URL</button>
	</div>

	<ul class="url-list">
		{#each seedUrls as url}
			<li class="url-item">
				<span>{url}</span>
				<button on:click={() => deleteUrl(url)}>Delete</button>
			</li>
		{/each}
	</ul>

	<button on:click={startCrawl}>Start Crawl</button>
</div>

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
</style>
