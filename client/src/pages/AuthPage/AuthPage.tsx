import LoginView from './SubviewsAuthPage/LoginView/LoginView.tsx'
import RegistrationView from './SubviewsAuthPage/RegistrationView/RegistrationView'
import BlinkingSpaceBGDiv from '../../components/BlinkingSpaceBGDiv/BlinkingSpaceBGDiv.tsx'
import { cx } from '../../utils/cx'
import styles from './AuthPage.module.css'

import { useAuthPage, useLoginNavigation, useRegistrationNavigation } from './useAuthPage'

export function AuthPage() {
	const { isLoginTabActive, setIsLoginTabActive } = useAuthPage()
	const { onLoginSuccess } = useLoginNavigation()
	const { onRegistrationSuccess } = useRegistrationNavigation()

	return (
		<div className={styles['login-page']}>
			<div className={styles['main-container']}>
				<div className={styles['empty-container']}>
					<BlinkingSpaceBGDiv />
					<div className={styles['empty-container-content']}>         {/* groups title + subtitle */}
						<h1 className={styles['page-title']}>QUIZSENDENCE</h1>
						<h1 className={cx(styles['page-title'], styles.gradient)}>GAME SHOW</h1>
						<p className={styles['page-subtitle']}>Real-time multiplayer trivia. Compete live, nominate your rivals, and climb to the top of the leaderboard. Every question is a spotlight moment.</p>
					</div>
				</div>

				<div className={styles['auth-container']}>
					<div className={styles['auth-content']}>
						<div className={styles['auth-title-container']}>
							<div className={styles['auth-title']}>
								{isLoginTabActive ? 'Welcome back' : 'Join the Show'}
							</div>
							<div className={styles['auth-subtitle']}>
								{isLoginTabActive ? 'Sign in to your account' : 'Create your free account'}
							</div>
						</div>

						<div className={styles['auth-tabs']}>
							<button className={cx(styles['auth-tab'], isLoginTabActive && styles.active)} onClick={() => setIsLoginTabActive(true)}>Sign In</button>
							<button className={cx(styles['auth-tab'], !isLoginTabActive && styles.active)} onClick={() => setIsLoginTabActive(false)}>Register</button>
						</div>
						{isLoginTabActive ? <LoginView onSuccess={onLoginSuccess} /> : <RegistrationView onSuccess={onRegistrationSuccess} />}
					</div>
				</div>

			</div>

		</div>
	)
}
