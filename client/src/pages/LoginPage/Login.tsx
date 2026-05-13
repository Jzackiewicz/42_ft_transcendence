import { useState } from 'react'
import LoginView from './LoginView.tsx'
import RegistrationView from'./RegistrationView.tsx'
import BlinkingSpaceBGDiv from '../../components/BlinkingSpaceBGDiv.tsx'
import './Login.css'


function LoginPage() {
    const [logginToggleState, setLoginTougle] = useState(true)
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