import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useLocation, useNavigate } from 'react-router-dom'

const LoginPage = () => {
	const { login } = useAuth()
	const [email, setEmail] = useState('adm@adm.ru')
	const [password, setPassword] = useState('123')
	const [error, setError] = useState<string | null>(null)

	const navigate = useNavigate()
	const location = useLocation()
	const from = (location.state as any)?.from?.pathname || '/'

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		setError(null)

		try {
			await login(email, password)
			navigate(from, { replace: true })
		} catch (err: any) {
			console.error(err)
			if (err.response && err.response.data?.detail) {
				setError(err.response.data.detail)
			} else {
				setError('Login failed. Try again.')
			}
		}
	}


	return (
		<form onSubmit={handleSubmit}>
			{error && <p style={{ color: 'red' }}>{error}</p>}
			<input
				type='email'
				value={email}
				onChange={e => setEmail(e.target.value)}
				placeholder='Email'
				required
			/>
			<input
				type='password'
				value={password}
				onChange={e => setPassword(e.target.value)}
				placeholder='Password'
				required
			/>
			<button type='submit'>Login</button>
		</form>
	)
}

export default LoginPage
