import React from 'react'
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'
import PrivateRoute from './components/PrivateRoute'
import { ActionContextProvider } from './context/ActionContext'
import { AuthProvider } from './context/AuthContext'
import Home from './pages/Home'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'

const App = () => {
	return (
		<React.StrictMode>
			<Router>
				<AuthProvider>
					<ActionContextProvider>
						<Routes>
							<Route
								path='/register'
								element={<RegisterPage />}
							/>
							<Route path='/login' element={<LoginPage />} />
							<Route element={<PrivateRoute />}>
								<Route path='/' element={<Home />} />
								<Route path='/c/:file_id' element={<Home />} />
							</Route>
						</Routes>
					</ActionContextProvider>
				</AuthProvider>
			</Router>
		</React.StrictMode>
	)
}

export default App
