import React from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import PrivateRoute from './components/Privateroute'
import RegisterPage from './pages/RegisterPage'
import LoginPage from './pages/LoginPage'
import Home from './pages/Home'
// import ChatPage from './pages/ChatPage'

const App = () => {
	return (
		<React.StrictMode>
			<AuthProvider>
				<Router>
					<Routes>
						<Route path='/register' element={<RegisterPage />} />
						<Route path='/login' element={<LoginPage />} />
						<Route element={<PrivateRoute />}>
							<Route path='/' element={<Home />} />
						</Route>
						{/* <Route path='/c/:file_id' element={<ChatPage />} /> */}
					</Routes>
				</Router>
			</AuthProvider>
		</React.StrictMode>
	)
}

export default App
