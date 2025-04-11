import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'

const LoginPage = () => {
	const { login } = useAuth()
	const [email, setEmail] = useState('')
	const [password, setPassword] = useState('')
	const [error, setError] = useState<string | null>(null)
	const [loading, setLoading] = useState(false)

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault()
		setError(null)
		setLoading(true)

		try {
			await login(email, password)
		} catch (err: any) {
			if (err.response?.data?.detail) {
				setError(err.response.data.detail)
			} else {
				setError('Login failed. Please check your credentials.')
			}
		} finally {
			setLoading(false)
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
			<button type='submit' disabled={loading}>
				{loading ? 'Logging in...' : 'Login'}
			</button>
		</form>
	)
}

export default LoginPage
