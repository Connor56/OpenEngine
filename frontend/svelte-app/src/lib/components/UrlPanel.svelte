<script lang="ts">
	import type { Url } from '$lib/types';
	import UrlCard from './UrlCard.svelte';
	import UrlEditModal from './UrlEditModal.svelte';
	import { createEventDispatcher } from 'svelte';
	import UrlDeleteModal from './UrlDeleteModal.svelte';

	// Props for the component
	export let selectedResource: string = '';
	export let coreResources: Url[];
	export let handleSelect: (index: number) => void;

	console.log(coreResources);

	const dispatch = createEventDispatcher();

	let showModal = false;
	let showDeleteModal = false;
	let url: Url;
	let edit: boolean = false;

	function handleEdit(editUrl: Url) {
		// Tell the modal this is edit mode
		edit = true;

		// Set the url to the provided url to edit
		url = editUrl;

		// Show the modal
		showModal = true;
	}

	function handleAdd() {
		// Set default values
		url = { url: '', faviconLocation: '', seeds: [] };

		edit = false;

		showModal = true;
	}

	function handleDelete(deleteUrl: Url) {
		// Set the url to delete
		url = deleteUrl;

		showDeleteModal = true;
	}

	function modalClose() {
		// Close the modals
		showModal = false;
		showDeleteModal = false;

		dispatch('close');
	}
</script>

<div class="url-panel">
	{#each coreResources as url, index}
		<UrlCard
			{url}
			on:delete={() => handleDelete(url)}
			on:select={() => handleSelect(index)}
			on:edit={() => handleEdit(url)}
			selected={url.url == selectedResource}
		/>
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
	{#if showModal}
		<UrlEditModal {url} {edit} on:close={modalClose} />
	{/if}
	{#if showDeleteModal}
		<UrlDeleteModal {url} on:close={modalClose} />
	{/if}
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
