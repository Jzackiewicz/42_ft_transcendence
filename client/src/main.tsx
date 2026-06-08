import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'

import { HomePage } from './pages/HomePage/HomePage.tsx'
import { AuthPage } from './pages/AuthPage/AuthPage.tsx'
import { GamePage } from './pages/GamePage/GamePage.tsx'

import { useUser, UserProvider } from './context/UserContext.tsx'

//Prevents navigating without authentication
function ProtectedRoute({ children }: { children: React.ReactElement }) {
    const { user, activeSessionUuid } = useUser()
    const location = useLocation()

    if (user === undefined) return null
    if (!user) return <Navigate to="/login" replace />

    // If there is an active session, force the user to stay in /lobby
    // This blocks manual navigation to /home
    if (activeSessionUuid && location.pathname !== '/lobby') {
        return <Navigate to="/lobby" state={{ sessionUuid: activeSessionUuid }} replace />
    }

    return children
}

// Prevents navigating to game lobby without an active session UUID in location state
function SessionProtectedRoute({ children }: { children: React.ReactElement }) {
    const { activeSessionUuid } = useUser()
    const location = useLocation()
    const sessionUuid = location.state?.sessionUuid || activeSessionUuid

    if (!sessionUuid) {
        return <Navigate to="/home" replace />
    }
    return children
}

// Prevents authenticated users from accessing login/registration pages
function PublicOnlyRoute({ children }: { children: React.ReactElement }) {
    const { user, activeSessionUuid } = useUser()
    if (user === undefined) return null
    if (user) {
        if (activeSessionUuid) return <Navigate to="/lobby" state={{ sessionUuid: activeSessionUuid }} replace />
        return <Navigate to="/home" replace />
    }
    return children
}

function RootRedirect() {
    const { user, activeSessionUuid } = useUser()
    if (user === undefined) return null
    if (user && activeSessionUuid) return <Navigate to="/lobby" state={{ sessionUuid: activeSessionUuid }} replace />
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
							<SessionProtectedRoute>
								<GamePage />
							</SessionProtectedRoute>
						</ProtectedRoute>
					} />
				</Routes>
			</BrowserRouter>
		</UserProvider>
	</React.StrictMode>,
)
