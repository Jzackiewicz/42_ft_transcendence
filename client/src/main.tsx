import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import { HomePage } from './pages/HomePage/HomePage.tsx'
import { AuthPage } from './pages/AuthPage/AuthPage.tsx'
import { GamePage } from './pages/GamePage/GamePage.tsx'
import { PrivacyPolicyPage } from './pages/PrivacyPolicy/PrivacyPolicyPage.tsx'
import { TermsOfServicePage } from './pages/TermsOfService/TermsOfServicePage.tsx'
import { Footer } from './components/Footer.tsx'
import { ErrorPage } from './pages/ErrorPage/ErrorPage.tsx'

import { UserProvider } from './context/UserContext.tsx'
import { PresenceProvider } from './context/PresenceContext.tsx'
import { ProtectedRoute, PublicOnlyRoute, SessionProtectedRoute, RootRedirect } from './components/NavGuards.tsx'

import './index.css'


ReactDOM.createRoot(document.getElementById('root')!).render(
	<React.StrictMode>
		<UserProvider>
			<PresenceProvider>
				<BrowserRouter>
					<div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
						<main style={{ flex: 1 }}>
							<Routes>
								<Route path="/" element={<RootRedirect />} />
								<Route path="/login" element={
									<PublicOnlyRoute>
										<AuthPage />
									</PublicOnlyRoute>
								} />
								<Route path="/privacy" element={<PrivacyPolicyPage />} />
								<Route path="/terms" element={<TermsOfServicePage />} />
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
						</main>
						<Footer />
					</div>
				</BrowserRouter>
			</PresenceProvider>
		</UserProvider>
	</React.StrictMode>,
)