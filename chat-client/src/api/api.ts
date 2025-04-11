import axios from 'axios'
import apiClient from '../utils/axios'

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

export const deleteFile = async (fileId: string) => {
	const response = await apiClient.delete(`/files/${fileId}`)
	return response.data
}

export const getFiles = async () => {
	const response = await apiClient.get('/files')
	return response.data
}

export const getFile = async (fileId: string) => {
	const response = await apiClient.get(`/files/${fileId}`)
	return response.data
}

export const getChatCompletions = async (messages: any[]) => {
	const response = await apiClient.post('/v1/chat/completions', { messages })
	return response.data
}
