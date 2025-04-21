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
		<div className='flex min-h-full flex-col justify-center px-6 py-12 lg:px-8 dark:bg-gray-700 h-screen text-gray-300'>
			<div className='mt-10 sm:mx-auto sm:w-full sm:max-w-sm'>
				<form className='space-y-6' onSubmit={handleSubmit}>
					{error && <p className='text-sm text-red-600'>{error}</p>}

					<div>
						<label
							htmlFor='email'
							className='block text-sm/6 font-medium'
						>
							Email address
						</label>
						<div className='mt-2'>
							<input
								id='email'
								type='email'
								value={email}
								onChange={e => setEmail(e.target.value)}
								required
								autoComplete='email'
								placeholder='Email'
								className='block w-full rounded-md bg-transparent px-3 py-1.5 text-base text-gray-400 border dark:border-gray-600 outline-1 -outline-offset-1 placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 sm:text-sm/6'
							/>
						</div>
					</div>

					<div>
						<div className='flex items-center justify-between'>
							<label
								htmlFor='password'
								className='block text-sm/6 font-medium'
							>
								Password
							</label>
						</div>
						<div className='mt-2'>
							<input
								id='password'
								type='password'
								value={password}
								onChange={e => setPassword(e.target.value)}
								required
								autoComplete='current-password'
								placeholder='Password'
								className='block w-full rounded-md bg-transparent px-3 py-1.5 text-base outline-1 -outline-offset-1 border dark:border-gray-600  placeholder:text-gray-400 focus:outline-2 focus:-outline-offset-2 sm:text-sm/6'
							/>
						</div>
					</div>

					<div>
						<button
							type='submit'
							className='flex w-full justify-center rounded-md bg-indigo-500 px-3 py-1.5 text-sm/6 font-semibold text-white shadow-xs hover:bg-indigo-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600'
						>
							Вход
						</button>
					</div>
				</form>
			</div>
		</div>
	)
}

export default LoginPage
