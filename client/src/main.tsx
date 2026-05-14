import React from 'react'
import ReactDOM from 'react-dom/client'
import {UserProvider} from './context/UserContext.tsx'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import HomePage from './pages/HomePage/HomePage.tsx'
import LoginPage from './pages/LoginPage/Login.tsx'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <UserProvider>
      <BrowserRouter>
        <Routes>
            <Route path="/" element={<Navigate to="/login" />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/home" element={<HomePage />} />
        </Routes>
      </BrowserRouter>
    </UserProvider>
  </React.StrictMode>,
)
