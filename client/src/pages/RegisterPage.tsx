import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { useNavigate } from 'react-router-dom'

const RegisterPage = () => {
	const { register } = useAuth()
	const [email, setEmail] = useState('')
	const [password, setPassword] = useState('')
	const navigate = useNavigate()

	const handleRegister = async (e: React.FormEvent) => {
		e.preventDefault()
		try {
			await register(email, password)
			navigate('/')
		} catch (err) {
			console.error('Registration failed', err)
		}
	}

	return (
		<div className='w-full max-w-md mx-auto'>
			<h1 className='text-center mb-4'>Register</h1>
			<form onSubmit={handleRegister}>
				<input
					type='email'
					placeholder='Email'
					value={email}
					onChange={e => setEmail(e.target.value)}
					className='w-full p-2 mb-4 border border-gray-300'
				/>
				<input
					type='password'
					placeholder='Password'
					value={password}
					onChange={e => setPassword(e.target.value)}
					className='w-full p-2 mb-4 border border-gray-300'
				/>
				<button
					type='submit'
					className='w-full p-2 bg-blue-500 text-white'
				>
					Register
				</button>
			</form>
		</div>
	)
}

export default RegisterPage
