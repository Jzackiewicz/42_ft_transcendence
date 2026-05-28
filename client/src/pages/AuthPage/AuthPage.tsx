import LoginView from './SubviewsAuthPage/LoginView/LoginView.tsx'
import RegistrationView from './SubviewsAuthPage/RegistrationView/RegistrationView'
import BlinkingSpaceBGDiv from '../../components/BlinkingSpaceBGDiv.tsx'
import './AuthPage.css'

import { useAuthPage, useLoginNavigation, useRegistrationNavigation } from './useAuthPage'

export function AuthPage() {
    const { isLoginTabActive, setIsLoginTabActive } = useAuthPage()
    const { onLoginSuccess } = useLoginNavigation()
    const { onRegistrationSuccess } = useRegistrationNavigation()

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
                                {isLoginTabActive ? 'Welcome back' : 'Join the Show'}
                            </div>
                            <div className="auth-subtitle">
                                {isLoginTabActive ? 'Sign in to your account' : 'Create your free account'}
                            </div>
                        </div>

                        <div className="auth-tabs">
                            <button className={isLoginTabActive ? 'auth-tab active' : 'auth-tab'} onClick={() => setIsLoginTabActive(true)}>Sign In</button>
                            <button className={isLoginTabActive ? 'auth-tab' : 'auth-tab active'} onClick={() => setIsLoginTabActive(false)}>Register</button>
                        </div>
                        {isLoginTabActive ? <LoginView onSuccess={onLoginSuccess} /> : <RegistrationView onSuccess={onRegistrationSuccess}/>}
                    </div>
                </div>

            </div>

        </div>
    )
}
