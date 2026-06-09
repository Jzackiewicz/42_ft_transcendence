import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useUser } from '../context/UserContext';

//Prevents navigating without authentication
export function ProtectedRoute({ children }: { children: React.ReactElement }) {
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
export function SessionProtectedRoute({ children }: { children: React.ReactElement }) {
	const { activeSessionUuid } = useUser()
	const location = useLocation()
	const sessionUuid = location.state?.sessionUuid || activeSessionUuid

	if (!sessionUuid) {
		return <Navigate to="/home" replace />
	}
	return children
}

// Prevents authenticated users from accessing login/registration pages
export function PublicOnlyRoute({ children }: { children: React.ReactElement }) {
	const { user, activeSessionUuid } = useUser()
	if (user === undefined) return null
	if (user) {
		if (activeSessionUuid) return <Navigate to="/lobby" state={{ sessionUuid: activeSessionUuid }} replace />
		return <Navigate to="/home" replace />
	}
	return children
}

export function RootRedirect() {
	const { user, activeSessionUuid } = useUser()
	if (user === undefined) return null
	if (user && activeSessionUuid) return <Navigate to="/lobby" state={{ sessionUuid: activeSessionUuid }} replace />
	return <Navigate to={user ? "/home" : "/login"} replace />
}
