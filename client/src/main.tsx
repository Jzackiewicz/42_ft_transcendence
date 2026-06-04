import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import { HomePage } from './pages/HomePage/HomePage.tsx'
import { AuthPage } from './pages/AuthPage/AuthPage.tsx'
import { GamePage } from './pages/GamePage/GamePage.tsx'
import { PrivacyPolicyPage } from './pages/PrivacyPolicy/PrivacyPolicyPage.tsx'
import { TermsOfServicePage } from './pages/TermsOfService/TermsOfServicePage.tsx'
import { Footer } from './components/Footer.tsx'

import { useUser, UserProvider } from './context/UserContext.tsx'

//Prevents navigating without authentication (if user is on https:site/login, disable navigating just by changing the route to the https:site/home)
function ProtectedRoute({ children }: { children: React.ReactNode }) {
	const { user } = useUser()
	if (user === undefined) return null
	if (!user) return <Navigate to="/login" />
	return children
}

ReactDOM.createRoot(document.getElementById('root')!).render(
	<React.StrictMode>
		<UserProvider>
			<BrowserRouter>
				<div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
					<main style={{ flex: 1 }}>
						<Routes>
							<Route path="/" element={<Navigate to="/login" />} />
							<Route path="/login" element={<AuthPage />} />
							<Route path="/privacy" element={<PrivacyPolicyPage />} />
							<Route path="/terms" element={<TermsOfServicePage />} />
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
					</main>
					<Footer />
				</div>
			</BrowserRouter>
		</UserProvider>
	</React.StrictMode>,
)
