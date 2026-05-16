import { useState, useEffect } from 'react'
import LoginView from './SubViewsLoginPage/LoginView/LoginView.tsx'
import RegistrationView from'./SubViewsLoginPage/RegistrationView/RegistrationView.tsx'
import BlinkingSpaceBGDiv from '../../components/BlinkingSpaceBGDiv.tsx'
import { initCSRF } from '../../api/apiWrapper.ts'
import './AuthPage.css'


function LoginPage() {
    const [isLoginTab, setIsLoginTab] = useState(true)

    useEffect(() => { 
        console.log("Initializing CSRF...")
        initCSRF()
            .catch(err => console.error("CSRF failed:", err))
    }, [])
    return (
        <div className="login-page">
            <div className="main-container">
                <div className="empty-container">
                    <BlinkingSpaceBGDiv/>
                    <div className="empty-container-content">         {/* groups title + subtitle */}
                        <h1 className="page-title">QUIZSENDENCE</h1>
                        <h1 className="page-title gradient">GAME SHOW</h1>
                        <p className="page-subtitle">Real-time multiplayer trivia. Compete live, nominate your rivals, and climb to the top of the leaderboard. Every question is a spotlight moment.</p>
                    </div>
                </div>

                <div className="auth-container">
                    <div className="auth-content">
                        <div className="auth-title-container">
                            <div className="auth-title">
                                {isLoginTab ? 'Welcome back' : 'Join the Show'}
                            </div>
                            <div className="auth-subtitle">
                                {isLoginTab ? 'Sign in to your account' : 'Create your free account'}
                            </div>
                        </div>

                        <div className="auth-tabs">
                            <button className={isLoginTab ? 'auth-tab active' : 'auth-tab'} onClick={() => setIsLoginTab(true)}>Sign In</button>
                            <button className={isLoginTab ? 'auth-tab' : 'auth-tab active'} onClick={() => setIsLoginTab(false)}>Register</button>
                        </div>
                        {isLoginTab ? <LoginView/> : <RegistrationView/>}
                    </div>
                </div>

            </div>

        </div>
    )
}

export default LoginPage