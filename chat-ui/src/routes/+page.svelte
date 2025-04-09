<script lang="ts">
	// import { goto } from "$app/navigation";
	// import { base } from "$app/paths";
	import { page } from "$app/state";
	import { env as envPublic } from "$env/dynamic/public";
	import ChatWindow from "$lib/components/chat/ChatWindow.svelte";
	// import { ERROR_MESSAGES, error } from "$lib/stores/errors";
	// import { pendingMessage } from "$lib/stores/pendingMessage";
	// import { useSettingsStore } from "$lib/stores/settings.js";
	// import { findCurrentModel } from "$lib/utils/models";
	import { onMount } from "svelte";

	// let { data } = $props();
	let loading = $state(false);
	// let files: File[] = $state([]);

	// const settings = useSettingsStore();

	async function createConversation(message: string) {
		
	}

	onMount(() => {
		// check if there's a ?q query param with a message
		const query = page.url.searchParams.get("q");
		if (query) createConversation(query);
	});
</script>

<svelte:head>
	<title>{envPublic.PUBLIC_APP_NAME}</title>
</svelte:head>

<ChatWindow
	on:message={(ev) => createConversation(ev.detail)}
	{loading}
/>
