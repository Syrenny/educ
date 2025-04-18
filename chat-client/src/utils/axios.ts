import axios from 'axios'
import { getUser } from './auth'
import { toast } from 'react-toastify'

const apiClient = axios.create({
	baseURL: 'http://localhost:8000',
	headers: {
		'Content-Type': 'application/json',
	},
})

// Automatically attach token
apiClient.interceptors.request.use(config => {
	const user = getUser()
	if (user) {
		config.headers.Authorization = `Bearer ${user["token"]}`
	}
	return config
})

apiClient.interceptors.response.use(
	response => response,
	error => {
		if (error.response?.status === 401) {
			window.location.href = '/login'
		}

        const message =
			error.response?.data?.detail ||
			error.response?.data?.message ||
			error.message
        toast.error(`Error: ${message}`)
        
		return Promise.reject(error)
	}
)

export default apiClient
