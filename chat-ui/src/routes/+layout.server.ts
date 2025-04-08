import axios from 'axios';
import type { LayoutServerLoad } from "./$types";
import { DEFAULT_SETTINGS } from "$lib/types/Settings";
import { env } from "$env/dynamic/private";

// Что здесь нужно загружать:
// - Историю сообщений
// - Файл
// - И прочее для отрисовки приложения

export const load: LayoutServerLoad = async ({ locals, depends, fetch }) => {
    const apiUrl = env.API_URL ? `${env.API_URL}/list_files` : "/list_files";

    try {
        const response = await axios.get(apiUrl);

        const { conversations } = response.data;
        return {
					nConversations: conversations.length,
					conversations: conversations,
					settings: {
						searchEnabled: !!(
							env.SERPAPI_KEY ||
							env.SERPER_API_KEY ||
							env.SERPSTACK_API_KEY ||
							env.SEARCHAPI_KEY ||
							env.YDC_API_KEY ||
							env.USE_LOCAL_WEBSEARCH ||
							env.SEARXNG_QUERY_URL ||
							env.BING_SUBSCRIPTION_KEY
						),
						ethicsModalAcceptedAt: null,
						activeModel: DEFAULT_SETTINGS.activeModel,
						hideEmojiOnSidebar: false,
						shareConversationsWithModelAuthors: DEFAULT_SETTINGS.shareConversationsWithModelAuthors,
						disableStream: DEFAULT_SETTINGS.disableStream,
						directPaste: DEFAULT_SETTINGS.directPaste,
					},
					user: locals.user && {
						id: locals.user._id.toString(),
						username: locals.user.username,
						avatarUrl: locals.user.avatarUrl,
						email: locals.user.email,
						logoutDisabled: locals.user.logoutDisabled,
						isAdmin: locals.user.isAdmin ?? false,
						isEarlyAccess: locals.user.isEarlyAccess ?? false,
					},
				};
    } catch (error) {
        console.error('Error while loading conversations', error);
        return {
            nConversations: 0,
            conversations: [],
            settings: {
                searchEnabled: false,
                ethicsModalAcceptedAt: null,
                activeModel: DEFAULT_SETTINGS.activeModel,
                hideEmojiOnSidebar: false,
                shareConversationsWithModelAuthors:
                DEFAULT_SETTINGS.shareConversationsWithModelAuthors,
                disableStream: DEFAULT_SETTINGS.disableStream,
                directPaste: DEFAULT_SETTINGS.directPaste,
            },
            user: locals.user && {
                id: locals.user._id.toString(),
                username: locals.user.username,
                avatarUrl: locals.user.avatarUrl,
                email: locals.user.email,
                logoutDisabled: locals.user.logoutDisabled,
                isAdmin: locals.user.isAdmin ?? false,
                isEarlyAccess: locals.user.isEarlyAccess ?? false,
            },
        };
    };
};
