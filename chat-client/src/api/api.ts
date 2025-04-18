import apiClient from '../utils/axios'
import type { Message } from '../types'
import { getUser } from '../utils/auth'
import OpenAI from 'openai'

export const loginUser = async (email: string, password: string) => {
	const response = await apiClient.post(
        '/login_user', 
        { 
            "email": email, 
            "password": password 
        }
    )
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
	const response = await apiClient.post(
        '/files', 
        formData, 
        {
		    headers: {
			    'Content-Type': 'multipart/form-data',
		    },
	    }
    )
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

    const baseURL = response.config.baseURL
    console.log("BaseURL", baseURL)
    const relativeURL = response.data
    const fullURL = new URL(relativeURL, baseURL).toString()
    console.log("FullURL", fullURL)
	return fullURL
}

export const createStreamChatCompletions = async (
	query: Message
): Promise<ReadableStreamDefaultReader<Uint8Array>> => {
    const user = getUser()
    console.log("action", query.shortcut?.action)
    console.log("content", query.shortcut?.content)
	const response = await fetch('http://localhost:8000/v1/chat/completions', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${user['token']}`,
		},
		body: JSON.stringify({
			messages: [
				{
					role: 'user',
					content: query.content,
				},
			],
			documents: [
				{
					filename: query.file_meta.filename,
					file_id: query.file_meta.file_id,
				},
			],
			shortcut: {
                action: query.shortcut?.action,
                content: query.shortcut?.content
            },
		}),
	})

    if (!response.ok) {
        if (response.status === 401) {
			window.location.href = '/login'
        }
    }

	if (!response.ok || !response.body) {
		throw new Error('Stream response error')
	}

	return response.body.getReader()
}


export const getHistory = async (fileId: string) => {
	const response = await apiClient.get(`/history/${fileId}`)
	return response.data
}

export const isIndexed = async (
	fileId: string
): Promise<boolean> => {
	const response = await apiClient.get(`/files/${fileId}/status`)
	return response.data
}
