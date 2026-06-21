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
		<div className={styles.mainContainer}>
				<div className={styles.emptyContainer}>
					<BlinkingSpaceBGDiv />
					<div className={styles.emptyContainerContent}>         {/* groups title + subtitle */}
						<h1 className={styles.pageTitle}>QUIZSENDENCE</h1>
						<h1 className={cx(styles.pageTitle, styles.gradient)}>GAME SHOW</h1>
						<p className={styles.pageSubtitle}>Real-time multiplayer trivia. Compete live, nominate your rivals, and climb to the top of the leaderboard. Every question is a spotlight moment.</p>
					</div>
				</div>

				<div className={styles.authContainer}>
					<div className={styles.authContent}>
						<div className={styles.authTitleContainer}>
							<div className={styles.authTitle}>
								{isLoginTabActive ? 'Welcome back' : 'Join the Show'}
							</div>
							<div className={styles.authSubtitle}>
								{isLoginTabActive ? 'Sign in to your account' : 'Create your free account'}
							</div>
						</div>

						<div className={styles.authTabs}>
							<button className={cx(styles.authTab, isLoginTabActive && styles.active)} onClick={() => setIsLoginTabActive(true)}>Sign In</button>
							<button className={cx(styles.authTab, !isLoginTabActive && styles.active)} onClick={() => setIsLoginTabActive(false)}>Register</button>
						</div>
						{isLoginTabActive ? <LoginView onSuccess={onLoginSuccess} /> : <RegistrationView onSuccess={onRegistrationSuccess} />}
					</div>
				</div>

		</div>
	)
}
