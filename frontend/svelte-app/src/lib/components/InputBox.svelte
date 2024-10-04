<script lang="ts">
	export let label: string;
	export let placeholder: string = '';
	export let showLabel: boolean = true;
</script>

<div class="input-box">
	{#if showLabel}
		<label for={label}>{label}</label>
	{/if}
	<input type="text" id={label} name={label} {placeholder} />
</div>

<style>
	.input-box {
		display: flex;
		flex-direction: column;
		margin-bottom: 20px;
		align-items: center;
	}

	label {
		font-size: 16px;
		font-weight: 500;
		margin-bottom: 5px;
	}

	input {
		width: 100%;
		padding: 10px;
		font-size: 16px;
		border-radius: 10px;
		border: 1px solid #dfe1e5;
	}

	input:focus {
		outline: none;
		border: 1px solid rgb(255, 255, 255);
		box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
	}

	input:hover {
		outline: none;
		border: 1px solid #ffffff;
		box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
	}
</style>
