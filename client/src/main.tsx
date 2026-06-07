import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import { HomePage } from './pages/HomePage/HomePage.tsx'
import { AuthPage } from './pages/AuthPage/AuthPage.tsx'
import { GamePage } from './pages/GamePage/GamePage.tsx'

import {useUser , UserProvider} from './context/UserContext.tsx'

function ProtectedRoute({ children, requireAuth }: { children: React.ReactNode, requireAuth: boolean }) {
    const { user } = useUser()
    if (user === undefined) return null
    if (requireAuth && !user) return <Navigate to="/login" />
    if (!requireAuth && user) return <Navigate to="/home" />
    return children
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <UserProvider>
      <BrowserRouter>
        <Routes>
            <Route path="/" element={<Navigate to="/login" />} />
            <Route path="/login" element={<ProtectedRoute requireAuth={false}><AuthPage /></ProtectedRoute>} />
            <Route path="/home"  element={<ProtectedRoute requireAuth={true}><HomePage /></ProtectedRoute>} />
            <Route path="/lobby" element={<ProtectedRoute requireAuth={true}><GamePage /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </UserProvider>
  </React.StrictMode>,
)
