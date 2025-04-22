import React, {
	createContext,
	useContext,
	useState,
	useEffect,
	ReactNode,
} from 'react'
import { loginUser, registerUser } from '../api/api'
import { setUser, getUser, removeUser } from '../utils/auth'

interface User {
	email: string
}

interface AuthContextType {
	user: User | null | undefined
	login: (email: string, password: string) => Promise<void>
	register: (email: string, password: string) => Promise<void>
	logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
	const [user, setUserState] = useState<User | null | undefined>(undefined)

	useEffect(() => {
		const init = async () => {
			const localUser = getUser()
            console.log("Reserved user: ", localUser)
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
			const user = { email }
			setUser(user.email)
			setUserState(user)
		} catch (err) {
			console.error('Login error:', err)
			throw err
		}
	}

	const register = async (email: string, password: string) => {
		try {
			const data = await registerUser(email, password)
			const user = { email }
			setUser(user.email)
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
