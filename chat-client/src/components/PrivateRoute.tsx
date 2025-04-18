import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const PrivateRoute = () => {
	const { user } = useAuth()
	const location = useLocation()

    if (user === undefined) {
		return <div>Loading...</div>
	}

    console.log("User in private route", user)
	if (!user) {
		return <Navigate to='/login' replace state={{ from: location }} />
	}

	return <Outlet />
}

export default PrivateRoute
