<script lang="ts">
	import FormButton from '$lib/components/FormButton.svelte';
	import InputBox from '$lib/components/InputBox.svelte';

	function handleSubmit(event: SubmitEvent) {
		alert('Form submitted!');
	}
</script>

<div class="login-center">
	<div class="login-container">
		<h1>Set Admin</h1>
		<form on:submit|preventDefault={handleSubmit}>
			<InputBox label="Username" placeholder="Username" showLabel={false} />
			<InputBox label="Password" placeholder="Password" showLabel={false} />
			<FormButton label="Set" />
		</form>
	</div>
</div>

<style>
	.login-center {
		display: flex;
		flex-direction: column;
		justify-content: center;
		align-items: center;
		height: 100vh;
	}

	.login-container {
		width: 400px;
		border: solid 1px #dfe1e5;
		border-radius: 10px;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.2);
	}

	h1 {
		align-content: center;
	}

	form {
		display: flex;
		flex-direction: column;
		padding: 20px;
	}
</style>
