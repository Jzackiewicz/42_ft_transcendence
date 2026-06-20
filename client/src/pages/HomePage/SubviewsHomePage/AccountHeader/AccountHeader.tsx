import { Badge } from '../../../../components/Badge/Badge'
import styles from './AccountHeader.module.css'
// Shared "home nav" button styles owned by the HomePage module.
import homeStyles from '../../HomePage.module.css'

interface AccountHeaderProps {
    username: string
    email: string
    setShowJoinModal: (bool: boolean) => void
    setShowRulesModal: (bool: boolean) => void
    handleCreateLobby: () => void
}

function AccountHeader({ username, email, setShowJoinModal, setShowRulesModal, handleCreateLobby }: AccountHeaderProps) {
    const initial = username[0]?.toUpperCase() ?? '?'

    return (
        <div className={styles['account-header']}>
            <div className={styles['account-avatar']}>{initial}</div>
            <div className={styles['account-info']}>
                <div className={styles['account-name']}>{username}</div>
                <div className={styles['account-email']}>{email}</div>
                <div className={styles['account-badges']}>
                    <Badge variant="human">Human</Badge>
                </div>
            </div>
            <button
                className={styles['home-nav-rules']}
                onClick={() => setShowRulesModal(true)}
                aria-label="How to play"
                title="How to play"
            >
                How to Play ?
            </button>
            <button className={homeStyles['home-nav-join']} onClick={() => setShowJoinModal(true)}> Join Game</button>
            <button className={homeStyles['home-nav-play']} onClick={handleCreateLobby}>▶ Play Now</button>
        </div>
    )
}

export default AccountHeader
