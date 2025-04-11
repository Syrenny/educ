import axios from 'axios'
import { getAuthToken } from './auth'

const apiClient = axios.create({
	baseURL: 'http://localhost:8000',
	headers: {
		'Content-Type': 'application/json',
	},
})

// Automatically attach token
apiClient.interceptors.request.use(config => {
	const token = getAuthToken()
	if (token) {
		config.headers.Authorization = `Bearer ${token}`
	}
	return config
})

export default apiClient
