import React from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { ShortcutContextProvider } from './context/ShortcutContext'
import PrivateRoute from './components/PrivateRoute'
import RegisterPage from './pages/RegisterPage'
import LoginPage from './pages/LoginPage'
import Home from './pages/Home'

const App = () => {
	return (
		<React.StrictMode>
			<AuthProvider>
				<ShortcutContextProvider>
					<Router>
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
					</Router>
				</ShortcutContextProvider>
			</AuthProvider>
		</React.StrictMode>
	)
}

export default App
