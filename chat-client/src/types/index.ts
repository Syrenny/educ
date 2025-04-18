

export type FileMeta = {
	filename: string
	file_id: string
    is_indexed: boolean
}

export type Message = {
    file_meta: FileMeta
    content: string
    is_user: boolean
    shortcut: Shortcut | null
}

export enum ShortcutAction {
	Translate = 'translate',
	Explain = 'explain',
	Ask = 'ask',
}

export type Shortcut = {
	content: string
	action: ShortcutAction
}