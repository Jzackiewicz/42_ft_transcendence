import { useState } from 'react'
import LoginView from './LoginView.tsx'
import RegistrationView from'./RegistrationView.tsx'
import Button from  '../../components/Button'
import './Login.css'


function LoginPage() {
    const [logginToggleState, setLoginTougle] = useState(true)
    return (
        <div className="login-page">
            <div className="main-container">
                <div className="empty-container">
                    <h1>QUIZDENSE</h1>
                </div>

                <div className="auth-container">
                    <div className="auth-content">
                        <div className="auth-title-container">
                            <div className="auth-title">
                                {logginToggleState ? 'Welcome back' : 'Join the Show'}
                            </div>
                            <div className="auth-subtitle">
                                {logginToggleState ? 'Sign in to your account' : 'Create your free account'}
                            </div>
                        </div>

                        <div className="auth-tabs">
                            <button className={logginToggleState ? 'auth-tab active' : 'auth-tab'} onClick={() => setLoginTougle(true)}>Sign In</button>
                            <button className={logginToggleState ? 'auth-tab' : 'auth-tab active'} onClick={() => setLoginTougle(false)}>Register</button>
                        </div>
                        {logginToggleState ? <LoginView /> : <RegistrationView/>}
                    </div>
                </div>

            </div>

        </div>
    )
}

export default LoginPage