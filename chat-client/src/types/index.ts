

export type FileMeta = {
	filename: string
	file_id: string
    is_indexed: boolean
}

export enum Action {
	Default = 'default',
	Translate = 'translate',
	Explain = 'explain',
	Ask = 'ask',
}

export type Message = {
    file_meta: FileMeta
    content: string
    is_user: boolean
    action: Action
    snippet: string | null
}


