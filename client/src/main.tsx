import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import { HomePage } from './pages/HomePage/HomePage.tsx'
import { AuthPage } from './pages/AuthPage/AuthPage.tsx'
import { GamePage } from './pages/GamePage/GamePage.tsx'
import { ErrorPage } from './pages/ErrorPage/ErrorPage.tsx'

import { UserProvider } from './context/UserContext.tsx'
import { ProtectedRoute, PublicOnlyRoute, SessionProtectedRoute, RootRedirect } from './components/NavGuards.tsx'


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
							<SessionProtectedRoute>
								<GamePage />
							</SessionProtectedRoute>
						</ProtectedRoute>
					} />
					<Route path="/error" element={<ErrorPage />} />
					<Route path="*" element={<Navigate to="/error" replace />} />
				</Routes>
			</BrowserRouter>
		</UserProvider>
	</React.StrictMode>,
)
