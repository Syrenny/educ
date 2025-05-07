import type { Message } from '../types'
import apiClient from '../utils/axios'

export const loginUser = async (email: string, password: string) => {
	const response = await apiClient.post('/login_user', {
		email: email,
		password: password,
	})
	return response.data
}

export const registerUser = async (email: string, password: string) => {
	const response = await apiClient.post('/register_user', { email, password })
	return response.data
}

export const fetchCurrentUser = async (): Promise<any> => {
	const response = await apiClient.get('/me')
	return response.data
}

export const uploadFile = async (files: File[]) => {
	const formData = new FormData()
	files.forEach(file => {
		formData.append('files', file)
	})
	const response = await apiClient.post('/files', formData, {
		headers: {
			'Content-Type': 'multipart/form-data',
		},
	})
	return response.data
}

export const getFileStatus = async (fileId: string) => {
	const response = await apiClient.get(`/files/${fileId}/status`)
	return response.data
}

export const deleteFile = async (fileId: string): Promise<boolean> => {
	const response = await apiClient.delete(`/files/${fileId}`)
	return response.data
}

export const getFiles = async () => {
	const response = await apiClient.get('/files')
	return response.data
}

export const getPDF = async (fileId: string): Promise<Uint8Array> => {
	const response = await apiClient.get(`/files/${fileId}`, {
		responseType: 'arraybuffer',
	})

	return new Uint8Array(response.data)
}

export const getURL = async (fileId: string): Promise<string> => {
	const response = await apiClient.get(`/files/${fileId}/signed-url`)
	const baseURL = apiClient.defaults.baseURL!
	const relativeURL = response.data
	const fullURL = new URL(relativeURL, baseURL).toString()
	return fullURL
}

export const getStreamID = async (query: Message): Promise<string> => {
	const response = await apiClient.post('/prepare_stream', {
		messages: [
			{
				role: 'user',
				content: query.content,
			},
		],
		file_id: query.file_meta.file_id,
		action: query.action,
		snippet: query.snippet,
	})
	return response.data
}

export const createStreamChatCompletions = async (
	query: Message,
	onData: (data: string) => void,
	onContext: (context: string[]) => void,
	onDone?: () => void,
	onError?: (e: any) => void
) => {
	const stream_id = await getStreamID(query)
	const eventSource = new EventSource(
		new URL(
			process.env.REACT_APP_API_BASE || '',
			`/v1/chat/completions?stream_id=${stream_id}`
		).toString(),
		{
			withCredentials: true,
		}
	)

	eventSource.addEventListener('chunk', event => {
		try {
			const parsedData = JSON.parse(event.data)
			const content = parsedData?.choices?.[0]?.delta?.content
			if (content) {
				onData(content)
			}
		} catch (error) {
			console.error('Error parsing event data:', error)
		}
	})

	eventSource.addEventListener('done', event => {
		eventSource.close()
		onDone?.()
	})

	eventSource.addEventListener('context', event => {
		const contextData = event.data ? JSON.parse(event.data) : []
		onContext(contextData)
	})

	eventSource.onerror = error => {
		console.error('SSE Error', error)
		eventSource.close()
		onError?.(error)
	}
}

export const getHistory = async (fileId: string) => {
	const response = await apiClient.get(`/history/${fileId}`)
	return response.data
}

export const isIndexed = async (fileId: string): Promise<boolean> => {
	const response = await apiClient.get(`/files/${fileId}/status`)
	return response.data
}
