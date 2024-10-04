<script lang="ts">
	export let label: string;
</script>

<button type="submit">{label}</button>

<style>
	button {
		width: 100%;
		padding: 10px;
		font-size: 16px;
		border-radius: 10px;
		border: 1px solid #dfe1e5;
		background-color: #ffffff;
		color: #368aff;
		cursor: pointer;
	}

	button:hover {
		background-color: #368aff;
		color: #ffffff;
		box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
	}
</style>
