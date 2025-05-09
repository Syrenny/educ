import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const PrivateRoute = () => {
	const { user, loading } = useAuth()
	const location = useLocation()

	if (loading) {
		return (
			<div className='flex items-center justify-center h-screen'>
				<div className='w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin' />
			</div>
		)
	}

	if (!user) {
		return <Navigate to='/login' replace state={{ from: location }} />
	}

	return <Outlet />
}

export default PrivateRoute
