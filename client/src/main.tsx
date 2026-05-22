import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import HomePage from './pages/HomePage/HomePage.tsx'
import AuthPage from './pages/AuthPage/AuthPage.tsx'

import {useUser , UserProvider} from './context/UserContext.tsx'

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
        <Routes>
            <Route path="/" element={<Navigate to="/login" />} />
            <Route path="/login" element={<AuthPage />} />
            <Route path="/home" element={
              <ProtectedRoute>
                <HomePage />
              </ProtectedRoute>
            } />
        </Routes>
      </BrowserRouter>
    </UserProvider>
  </React.StrictMode>,
)
