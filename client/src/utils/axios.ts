import axios from 'axios'
import { toast } from 'react-toastify'

const apiClient = axios.create({
	baseURL: process.env.REACT_APP_API_BASE,
	headers: {
		'Content-Type': 'application/json',
	},
})

apiClient.defaults.withCredentials = true

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
