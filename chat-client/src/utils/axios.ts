import axios from 'axios'
import { getUser } from './auth'

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

export default apiClient
