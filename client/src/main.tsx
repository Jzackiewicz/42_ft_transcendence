import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './devDraft/App.tsx'
import LoginPage from './pages/LoginPage/Login.tsx'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {/* <App /> */}
    <LoginPage />
  </React.StrictMode>,
)
