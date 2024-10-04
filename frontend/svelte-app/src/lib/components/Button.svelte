<script lang="ts">
	import { hasContext, onMount } from 'svelte';

	export let label: string;
	export let handleClick: (event: Event) => void;
	export let color: string = '#368aff';
	export let backgroundColor: string = '#ffffff';
	export let border: string = '#dfe1e5';
	export let hoverColor: string = '#ffffff';
	export let hoverBackgroundColor: string = '#368aff';

	let theButton: HTMLButtonElement;

	onMount(() => {
		theButton.style.border = '1px solid ' + border;
		theButton.style.backgroundColor = backgroundColor;
		theButton.style.color = color;
	});

	function handleMouseOver(event: Event) {
		theButton.style.backgroundColor = hoverBackgroundColor;
		theButton.style.color = hoverColor;
	}

	function handleMouseOut(event: Event) {
		theButton.style.backgroundColor = backgroundColor;
		theButton.style.color = color;
	}
</script>

<button
	bind:this={theButton}
	on:click={handleClick}
	on:mouseenter={handleMouseOver}
	on:mouseleave={handleMouseOut}>{label}</button
>

<style>
	button {
		width: 100%;
		padding: 10px;
		font-size: 16px;
		border-radius: 10px;
		cursor: pointer;
		margin: 10px;
	}

	button:hover {
		background-color: #368aff;
		color: #ffffff;
		box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
	}
</style>
