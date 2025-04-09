<script lang="ts">
	import { run } from "svelte/legacy";

	import "../styles/main.css";

	import { goto } from "$app/navigation";
	import { base } from "$app/paths";
	import { page } from "$app/stores";
	import { onDestroy, onMount, untrack } from "svelte";

	import { env as envPublic } from "$env/dynamic/public";

	import { error } from "$lib/stores/errors";

	import { shareConversation } from "$lib/shareConversation";

	import LoginModal from "$lib/components/LoginModal.svelte";
	import MobileNav from "$lib/components/MobileNav.svelte";
	import NavMenu from "$lib/components/NavMenu.svelte";
	import OverloadedModal from "$lib/components/OverloadedModal.svelte";
	import PdfReader from '$lib/components/PDFReader.svelte';
	import Toast from "$lib/components/Toast.svelte";
	import { loginModalOpen } from "$lib/stores/loginModal";
	import titleUpdate from "$lib/stores/titleUpdate";
	import { isHuggingChat } from "$lib/utils/isHuggingChat";
    import ChatWindow from '$lib/components/chat/ChatWindow.svelte';
    import { DEFAULT_SETTINGS } from "$lib/types/Settings";

    import axios from "axios";

    import { user } from "$lib/stores/user"


    // interface FileMeta {
    //     file_id: string;
    //     name: string;
    // }

    // interface Message {
    //     content: string;
    //     timestamp: string;
    // }

    // interface Conversation {
    //     file: FileMeta;
    //     messages: Message[];
    // } 

	// let conversations: Conversation[] = $state([]);
	// let overloadedModalOpen = $state(false);
	// let errorToastTimeout: ReturnType<typeof setTimeout>;
	// let currentError: string | undefined = $state();

    // onMount(async () => {
    //     const apiBase = env.API_URL || "";
    //     let currentUser = $user.token;

    //     try {
    //         // 1. Get file list
    //         const filesResponse = await axios.get(`${apiBase}/files`, {
    //             headers: {
    //                 Authorization: `Bearer ${token}`,
    //             },
    //         });

    //         const fileMetas: { file_id: string; name: string }[] = filesResponse.data.files;

    //         // 2. Get messages for each file_id
    //         conversations = await Promise.all(
    //             fileMetas.map(async (fileMeta) => {
    //                 try {
    //                     const messagesResponse = await axios.get(`${apiBase}/history/${fileMeta.file_id}`, {
    //                         headers: {
    //                             Authorization: `Bearer ${token}`,
    //                         },
    //                     });
    //                     return {
    //                         file: fileMeta,
    //                         messages: messagesResponse.data,
    //                     };
    //                 } catch (err) {
    //                     console.error(`Failed to load messages for file ${fileMeta.file_id}`, err);
    //                     return {
    //                         file: fileMeta,
    //                         messages: [],
    //                     };
    //                 }
    //             })
    //         );
             
            
    //     } catch (error) {
    //         console.error("Error while loading conversations", error);
    //     }
    // });

	// async function onError() {
	// 	// If a new different error comes, wait for the current error to hide first
	// 	if ($error && currentError && $error !== currentError) {
	// 		clearTimeout(errorToastTimeout);
	// 		currentError = undefined;
	// 		await new Promise((resolve) => setTimeout(resolve, 300));
	// 	}

	// 	currentError = $error;

	// 	if (currentError === "Model is overloaded") {
	// 		overloadedModalOpen = true;
	// 	}
	// 	errorToastTimeout = setTimeout(() => {
	// 		$error = undefined;
	// 		currentError = undefined;
	// 	}, 10000);
	// }

	// async function deleteConversation(id: string) {
	// 	try {
	// 		const res = await fetch(`${base}/conversation/${id}`, {
	// 			method: "DELETE",
	// 			headers: {
	// 				"Content-Type": "application/json",
	// 			},
	// 		});

	// 		if (!res.ok) {
	// 			$error = "Error while deleting conversation, try again.";
	// 			return;
	// 		}

	// 		conversations = conversations.filter((conv) => conv.file.file_id !== id);

	// 		if ($page.params.id === id) {
	// 			await goto(`${base}/`, { invalidateAll: true });
	// 		}
	// 	} catch (err) {
	// 		console.error(err);
	// 		$error = String(err);
	// 	}
	// }

	// onDestroy(() => {
	// 	clearTimeout(errorToastTimeout);
	// });

	// run(() => {
	// 	if ($error) onError();
	// });


	// let mobileNavTitle = $derived(
	// 	["/models", "/assistants", "/privacy", "/tools"].includes($page.route.id ?? "")
	// 		? ""
	// 		: conversations.find((conv) => conv.file.file_id === $page.params.id)?.file.name
	// );
</script>

<svelte:head>
	<title>{envPublic.PUBLIC_APP_NAME}</title>
	<meta name="description" content="The first open source alternative to ChatGPT. 💪" />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:site" content="@huggingface" />

	<!-- use those meta tags everywhere except on the share assistant page -->
	<!-- feel free to refacto if there's a better way -->
	{#if !$page.url.pathname.includes("/assistant/") && $page.route.id !== "/assistants" && !$page.url.pathname.includes("/models/") && !$page.url.pathname.includes("/tools")}
		<meta property="og:title" content={envPublic.PUBLIC_APP_NAME} />
		<meta property="og:type" content="website" />
		<meta property="og:url" content="{envPublic.PUBLIC_ORIGIN || $page.url.origin}{base}" />
		<meta
			property="og:image"
			content="{envPublic.PUBLIC_ORIGIN ||
				$page.url.origin}{base}/{envPublic.PUBLIC_APP_ASSETS}/thumbnail.png"
		/>
		<meta property="og:description" content={envPublic.PUBLIC_APP_DESCRIPTION} />
	{/if}
	<link
		rel="icon"
		href="{envPublic.PUBLIC_ORIGIN ||
			$page.url.origin}{base}/{envPublic.PUBLIC_APP_ASSETS}/favicon.ico"
		sizes="32x32"
	/>
	<link
		rel="icon"
		href="{envPublic.PUBLIC_ORIGIN ||
			$page.url.origin}{base}/{envPublic.PUBLIC_APP_ASSETS}/icon.svg"
		type="image/svg+xml"
	/>
	<link
		rel="apple-touch-icon"
		href="{envPublic.PUBLIC_ORIGIN ||
			$page.url.origin}{base}/{envPublic.PUBLIC_APP_ASSETS}/apple-touch-icon.png"
	/>
	<link
		rel="manifest"
		href="{envPublic.PUBLIC_ORIGIN ||
			$page.url.origin}{base}/{envPublic.PUBLIC_APP_ASSETS}/manifest.json"
	/>

	{#if envPublic.PUBLIC_PLAUSIBLE_SCRIPT_URL && envPublic.PUBLIC_ORIGIN}
		<script
			defer
			data-domain={new URL(envPublic.PUBLIC_ORIGIN).hostname}
			src={envPublic.PUBLIC_PLAUSIBLE_SCRIPT_URL}
		></script>
	{/if}

	{#if envPublic.PUBLIC_APPLE_APP_ID}
		<meta name="apple-itunes-app" content={`app-id=${envPublic.PUBLIC_APPLE_APP_ID}`} />
	{/if}
</svelte:head>

{#if $loginModalOpen}
	<LoginModal
		on:close={() => {
			$loginModalOpen = false;
		}}
	/>
{/if}

<!-- {#if overloadedModalOpen && isHuggingChat}
	<OverloadedModal onClose={() => (overloadedModalOpen = false)} />
{/if} -->
<div class="w-screen h-full flex">
    <div class="w-2/3 h-screen">
        <PdfReader/>
    </div>
    <div class="w-[5px] bg-gray-300 h-full resize-x cursor-ew-resize"></div>

    <div
        class="grid h-full w-1/3 right-0 grid-cols-1 grid-rows-[auto,1fr] overflow-hidden text-smd dark:text-gray-300 md:grid-rows-[1fr]"
    >
        <slot></slot>
        <!-- <MobileNav isOpen={isNavOpen} on:toggle={(ev) => (isNavOpen = ev.detail)} title={mobileNavTitle}>
            <NavMenu
                {conversations}
                user={data.user}
                canLogin={data.user === undefined && data.loginEnabled}
                on:shareConversation={(ev) => shareConversation(ev.detail.id, ev.detail.title)}
                on:deleteConversation={(ev) => deleteConversation(ev.detail)}
                on:editConversationTitle={(ev) => editConversationTitle(ev.detail.id, ev.detail.title)}
            />
        </MobileNav>
        <nav
            class="fixed h-full right-0 grid max-h-screen grid-cols-1 z-30 grid-rows-[auto,1fr,auto] bg-gray-50 overflow-hidden *:w-[290px] max-md:hidden {!isNavCollapsed
                ? 'right-[0px]'
                : 'right-[-290px]'} *:transition-transform"
        >
            <NavMenu
                {conversations}
                user={data.user}
                canLogin={data.user === undefined && data.loginEnabled}
                on:shareConversation={(ev) => shareConversation(ev.detail.id, ev.detail.title)}
                on:deleteConversation={(ev) => deleteConversation(ev.detail)}
                on:editConversationTitle={(ev) => editConversationTitle(ev.detail.id, ev.detail.title)}
            />
        </nav> -->
        <!-- {#if currentError}
            <Toast message={currentError} />
        {/if} -->
    </div>

</div>
