import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import { HomePage } from './pages/HomePage/HomePage.tsx'
import { AuthPage } from './pages/AuthPage/AuthPage.tsx'
import { GamePage } from './pages/GamePage/GamePage.tsx'

import { useUser, UserProvider } from './context/UserContext.tsx'

//Prevents navigating without authentication
function ProtectedRoute({ children }: { children: React.ReactElement }) {
	const { user } = useUser()
	if (user === undefined) return null
	if (!user) return <Navigate to="/login" replace />
	return children
}

// Prevents authenticated users from accessing login/registration pages
function PublicOnlyRoute({ children }: { children: React.ReactElement }) {
	const { user } = useUser()
	if (user === undefined) return null
	if (user) return <Navigate to="/home" replace />
	return children
}

function RootRedirect() {
	const { user } = useUser()
	if (user === undefined) return null
	return <Navigate to={user ? "/home" : "/login"} replace />
}
ReactDOM.createRoot(document.getElementById('root')!).render(
	<React.StrictMode>
		<UserProvider>
			<BrowserRouter>
				<Routes>
					<Route path="/" element={<RootRedirect />} />
					<Route path="/login" element={
						<PublicOnlyRoute>
							<AuthPage />
						</PublicOnlyRoute>
					} />
					<Route path="/home" element={
						<ProtectedRoute>
							<HomePage />
						</ProtectedRoute>
					} />
					<Route path="/lobby" element={
						<ProtectedRoute>
							<GamePage />
						</ProtectedRoute>
					} />
				</Routes>
			</BrowserRouter>
		</UserProvider>
	</React.StrictMode>,
)
