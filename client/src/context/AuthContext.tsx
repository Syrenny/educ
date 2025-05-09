import {
	createContext,
	ReactNode,
	useContext,
	useEffect,
	useState,
} from 'react'
import {
	deleteCookie,
	fetchCurrentUser,
	loginUser,
	registerUser,
} from '../api/api'
import { useLocation } from 'react-router-dom'

interface User {
	email: string
}

interface AuthContextType {
	user: User | null
	loading: boolean
	login: (email: string, password: string) => Promise<void>
	register: (email: string, password: string) => Promise<void>
	logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
	const [user, setUserState] = useState<User | null>(null)
	const [loading, setLoading] = useState(true)
    const location = useLocation()

	useEffect(() => {
		const skipPaths = ['/login', '/register']
		if (skipPaths.includes(location.pathname)) {
			setLoading(false)
			return
		}

		const init = async () => {
			try {
				const data = await fetchCurrentUser()
				setUserState({ email: data.email })
			} catch (error) {
				setUserState(null)
				console.error('Invalid token or failed to fetch user:', error)
			} finally {
				setLoading(false)
			}
		}
		init()
	}, [location.pathname])

	const login = async (email: string, password: string) => {
		const data = await loginUser(email, password)
		setUserState({ email: data.email })
        setLoading(false)
	}

	const register = async (email: string, password: string) => {
		const data = await registerUser(email, password)
		setUserState({ email: data.email })
        setLoading(false)
	}

	const logout = async () => {
		try {
			await deleteCookie()
		} catch (err) {
			console.error('Error while logout:', err)
		}
	}

	return (
		<AuthContext.Provider
			value={{ user, loading, login, register, logout }}
		>
			{children}
		</AuthContext.Provider>
	)
}

export const useAuth = () => {
	const context = useContext(AuthContext)
	if (!context) {
		throw new Error('useAuth must be used within an AuthProvider')
	}
	return context
}
