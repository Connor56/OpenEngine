<script lang="ts">
	import type { Url } from '$lib/types';

	export let url: Url;
	export let handleDelete: (Event: Event) => void;
	export let handleSelect: (Event: Event) => void;
</script>

<div class="url-card">
	<div class="url-card-content" on:click={handleSelect}>
		<img class="url-card-favicon" src={url.faviconLocation} alt="favicon" />
		<a class="url-card-title">{url.url}</a>
		<div class="interactions">
			<a class="url-card-title" href={url.url}>
				<svg class="external-link" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
					<path
						d="M36 26V38C36 39.0609 35.5786 40.0783 34.8284 40.8284C34.0783 41.5786 33.0609 42 32 42H10C8.93913 42 7.92172 41.5786 7.17157 40.8284C6.42143 40.0783 6 39.0609 6 38V16C6 14.9391 6.42143 13.9217 7.17157 13.1716C7.92172 12.4214 8.93913 12 10 12H22M30 6H42M42 6V18M42 6L20 28"
						stroke-width="4"
						stroke-linecap="round"
						stroke-linejoin="round"
					/>
				</svg>
			</a>
			<svg
				class="delete-button"
				on:click={handleDelete}
				viewBox="0 0 24 24"
				xmlns="http://www.w3.org/2000/svg"
			>
				<path
					d="M7 21C6.45 21 5.97917 20.8042 5.5875 20.4125C5.19583 20.0208 5 19.55 5 19V6H4V4H9V3H15V4H20V6H19V19C19 19.55 18.8042 20.0208 18.4125 20.4125C18.0208 20.8042 17.55 21 17 21H7ZM17 6H7V19H17V6ZM9 17H11V8H9V17ZM13 17H15V8H13V17Z"
				/>
			</svg>
		</div>
	</div>
</div>

<style>
	.url-card {
		display: flex;
		flex-direction: column;
		border-radius: 10px;
		padding: 10px;
		margin-bottom: 10px;
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
