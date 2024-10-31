<script lang="ts">
	import { createEventDispatcher, onMount } from 'svelte';
	import type { Url } from '$lib/types';

	export let url: Url;
	export let edit: boolean;

	let API_URL: string;

	const dispatch = createEventDispatcher();

	async function handleSubmit(event: SubmitEvent) {
		// Get the event target as an element
		const element = event.target! as HTMLFormElement;

		// Extract the new url from the form
		let newUrl = element.url.value;

		let response;

		if (edit) {
			// Update the url via the API
			response = await fetch(`${API_URL}/update-seed-url`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${localStorage.getItem('token')}`
				},
				body: JSON.stringify({
					old_url: url.url,
					url: newUrl
				})
			});
		} else {
			// Add the url via the API
			response = await fetch(`${API_URL}/add-seed-url`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					Authorization: `Bearer ${localStorage.getItem('token')}`
				},
				body: JSON.stringify({
					url: newUrl
				})
			});
		}

		console.log(await response.json());
		dispatch('close');
	}

	onMount(async () => {
		// Get the API_URL
		const reponse = await fetch('/env.json');
		const env = await reponse.json();
		API_URL = env.API_URL;

		console.log(API_URL);
	});
</script>

<div class="url-edit-modal">
	<div class="url-edit-modal-content">
		<div class="modal-header">
			<h2>Edit Url</h2>
			<button on:click={() => dispatch('close')}>
				<svg
					width="30"
					height="30"
					viewBox="0 0 48 48"
					fill="none"
					xmlns="http://www.w3.org/2000/svg"
					class="close-button"
				>
					<path
						d="M30 18L18 30M18 18L30 30M44 24C44 35.0457 35.0457 44 24 44C12.9543 44 4 35.0457 4 24C4 12.9543 12.9543 4 24 4C35.0457 4 44 12.9543 44 24Z"
						stroke-width="4"
						stroke-linecap="round"
						stroke-linejoin="round"
					/>
				</svg>
			</button>
		</div>

		<form on:submit|preventDefault={handleSubmit}>
			<input type="text" name="url" placeholder="Url" value={url.url} />
			<button type="submit" class="submit-button">Done</button>
		</form>
	</div>
</div>

<style>
	.url-edit-modal {
		position: fixed;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		background-color: rgba(0, 0, 0, 0.5);
		display: flex;
		justify-content: center;
		align-items: center;
		z-index: 10;
	}

	.url-edit-modal-content {
		background-color: white;
		border-radius: 1.5rem;
		padding: 1.5rem;
		width: min-content;
		height: min-content;
	}

	.modal-header {
		display: flex;
		flex-direction: row;
		justify-content: space-between;
		margin-bottom: 1rem;
		align-items: start;
	}

	h2 {
		margin-top: 0px;
	}

	.close-button {
		stroke: #757575;
	}

	.close-button:hover {
		stroke: #ff0000;
		cursor: pointer;
	}

	form {
		display: flex;
		flex-direction: column;
		align-items: center;
		row-gap: 1rem;
		font-size: 2rem;
		margin: 0rem 1rem;
	}

	button {
		all: unset;
	}

	input {
		width: 15rem;
		font-size: 1rem;
		border: 1px solid #dfe1e5;
		border-radius: 0.5rem;
		padding: 0.5rem;
	}

	.submit-button {
		background-color: #28b828;
		color: white;
		border: none;
		padding: 0.5rem 1rem;
		border-radius: 0.5rem;
		cursor: pointer;
		width: fit-content;
		font-size: 1rem;
	}

	.submit-button:hover {
		background-color: #1e9c1e;
	}
</style>
