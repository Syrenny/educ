import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { loginUser, registerUser, fetchCurrentUser } from '../api/api'
import { setAuthToken, getAuthToken, removeAuthToken } from '../utils/auth'
import jwtDecode from 'jwt-decode'

interface AuthContextType {
	user: any
	login: (email: string, password: string) => Promise<void>
	register: (email: string, password: string) => Promise<void>
	logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
	const [user, setUser] = useState<any | null>(null)

    useEffect(() => {
		const init = async () => {
			const token = getAuthToken()
			if (token) {
				try {
					const currentUser = await fetchCurrentUser()
					setUser(currentUser)
				} catch (error) {
					console.error(
						'Invalid token or failed to fetch user:',
						error
					)
					removeAuthToken()
					setUser(null)
				}
			}
		}
		init()
	}, [])

	const login = async (email: string, password: string) => {
		const data = await loginUser(email, password)
		setUser(data.user)
		setAuthToken(data.token)
	}

	const register = async (email: string, password: string) => {
		const data = await registerUser(email, password)
		setUser(data.user)
		setAuthToken(data.token)
	}

	const logout = () => {
		setUser(null)
		removeAuthToken()
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
