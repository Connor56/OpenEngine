<script lang="ts">
	import type { Url } from '$lib/types';
	import { createEventDispatcher } from 'svelte';

	export let url: Url;
	export let selected: boolean = false;

	const dispatch = createEventDispatcher();

	function handleDelete() {
		dispatch('delete'); // Dispatch a 'delete' event to the parent
	}

	function handleSelect() {
		dispatch('select');
	}

	function handleEdit() {
		dispatch('edit');
	}
</script>

<div class="url-card {selected ? 'selected' : ''}">
	<button on:click={handleSelect}>
		<div class="url-card-content">
			<img class="url-card-favicon" src={url.faviconLocation} alt="favicon" />
			<a class="url-card-title">{url.url}</a>
			<div class="interactions">
				<button on:click={handleEdit} class="edit-button">
					<svg
						width="23"
						height="23"
						viewBox="0 0 80 80"
						fill="none"
						xmlns="http://www.w3.org/2000/svg"
					>
						<path
							d="M56.6668 10C57.5422 9.12453 58.5816 8.43006 59.7254 7.95626C60.8693 7.48245 62.0953 7.23859 63.3334 7.23859C64.5715 7.23859 65.7975 7.48245 66.9414 7.95626C68.0853 8.43006 69.1246 9.12453 70.0001 10C70.8756 10.8755 71.57 11.9148 72.0438 13.0587C72.5176 14.2026 72.7615 15.4286 72.7615 16.6667C72.7615 17.9048 72.5176 19.1308 72.0438 20.2746C71.57 21.4185 70.8756 22.4579 70.0001 23.3333L25.0001 68.3333L6.66675 73.3333L11.6667 55L56.6668 10Z"
							stroke-width="7"
							stroke-linecap="round"
							stroke-linejoin="round"
						/>
					</svg>
				</button>
				<a class="url-card-title" href={url.url} target="_blank">
					<svg class="external-link" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
						<path
							d="M36 26V38C36 39.0609 35.5786 40.0783 34.8284 40.8284C34.0783 41.5786 33.0609 42 32 42H10C8.93913 42 7.92172 41.5786 7.17157 40.8284C6.42143 40.0783 6 39.0609 6 38V16C6 14.9391 6.42143 13.9217 7.17157 13.1716C7.92172 12.4214 8.93913 12 10 12H22M30 6H42M42 6V18M42 6L20 28"
							stroke-width="4"
							stroke-linecap="round"
							stroke-linejoin="round"
						/>
					</svg>
				</a>
				<button on:click={handleDelete}>
					<svg class="delete-button" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
						<path
							d="M7 21C6.45 21 5.97917 20.8042 5.5875 20.4125C5.19583 20.0208 5 19.55 5 19V6H4V4H9V3H15V4H20V6H19V19C19 19.55 18.8042 20.0208 18.4125 20.4125C18.0208 20.8042 17.55 21 17 21H7ZM17 6H7V19H17V6ZM9 17H11V8H9V17ZM13 17H15V8H13V17Z"
						/>
					</svg>
				</button>
			</div>
		</div>
	</button>
</div>

<style>
	button {
		all: unset;
	}

	.edit-button {
		margin-right: 10px;
		stroke: #757575;
	}

	.edit-button:hover {
		cursor: pointer;
		stroke: black;
	}

	.url-card {
		display: flex;
		flex-direction: column;
		border-radius: 10px;
		padding: 10px;
		margin-bottom: 10px;
	}

	.url-card.selected {
		/* background-color: #e5f7ff; */
		border: 1px solid #bbbbbb;
	}

	.url-card:hover {
		cursor: pointer;
		background-color: #f5f5f5;
		box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
	}

	.url-card-favicon {
		width: 20px;
		height: 20px;
		margin-right: 10px;
		border-radius: 50%;
	}

	.url-card-content {
		display: flex;
		flex-direction: row;
		align-items: center;
	}

	.url-card-title {
		font-size: 16px;
		font-weight: bold;
	}

	.interactions {
		display: flex;
		flex-direction: row;
		justify-content: right;
		width: 100%;
	}

	.external-link {
		stroke: #757575;
		width: 25px;
		height: 25px;
		right: 20px;
		fill: none;
	}

	.external-link:hover {
		stroke: #368aff;
	}

	.delete-button {
		fill: #757575;
		width: 28px;
		height: 28px;
		right: 20px;
		margin-left: 5px;
	}

	.delete-button:hover {
		fill: #ff0000;
	}
</style>
