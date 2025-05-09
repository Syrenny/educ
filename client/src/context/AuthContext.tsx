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

	useEffect(() => {
		const init = async () => {
			try {
				const data = await fetchCurrentUser()
				setUserState({ email: data.email })
			} catch (error) {
				console.error('Invalid token or failed to fetch user:', error)
			} finally {
				setLoading(false)
			}
		}
		init()
	}, [])

	const login = async (email: string, password: string) => {
		try {
			const data = await loginUser(email, password)
			setUserState({ email: data.email })
		} catch (err) {
			console.error('Login error:', err)
			throw err
		}
	}

	const register = async (email: string, password: string) => {
		try {
			const data = await registerUser(email, password)
			setUserState({ email: data.email })
		} catch (err) {
			console.error('Registration error:', err)
			throw err
		}
	}

	const logout = async () => {
		try {
			await deleteCookie()
			setUserState(null)
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
