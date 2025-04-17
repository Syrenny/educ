

export type FileMeta = {
	filename: string
	file_id: string
    is_indexed: boolean
}

export type Message = {
    file_meta: FileMeta
    content: string
    is_user: boolean
}