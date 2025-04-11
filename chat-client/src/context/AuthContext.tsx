import React, {
	createContext,
	useContext,
	useState,
	useEffect,
	ReactNode,
} from 'react'
import { loginUser, registerUser, fetchCurrentUser } from '../api/api'
import { setUser, getUser, removeUser } from '../utils/auth'

interface User {
	email: string
	token: string
}

interface AuthContextType {
	user: User | null
	login: (email: string, password: string) => Promise<void>
	register: (email: string, password: string) => Promise<void>
	logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
	const [user, setUserState] = useState<User | null>(null)

	useEffect(() => {
		const init = async () => {
			const localUser = getUser()
			if (localUser) {
				try {
					setUserState(localUser)
				} catch (error) {
					console.error(
						'Invalid token or failed to fetch user:',
						error
					)
					removeUser()
					setUserState(null)
				}
			}
		}
		init()
	}, [])

	const login = async (email: string, password: string) => {
		try {
			const data = await loginUser(email, password)
			const user = { email, token: data.token }
			setUser(user.email, user.token)
			setUserState(user)
		} catch (err) {
			console.error('Login error:', err)
			throw err
		}
	}

	const register = async (email: string, password: string) => {
		try {
			const data = await registerUser(email, password)
			const user = { email, token: data.token }
			setUser(user.email, user.token)
			setUserState(user)
		} catch (err) {
			console.error('Registration error:', err)
			throw err
		}
	}

	const logout = () => {
		setUserState(null)
		removeUser() 
	}

	return (
		<AuthContext.Provider value={{ user, login, register, logout }}>
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
