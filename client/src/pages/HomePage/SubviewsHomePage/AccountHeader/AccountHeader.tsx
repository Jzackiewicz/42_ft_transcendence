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
        <div className={styles.accountHeader}>
            <div className={styles.accountAvatar}>{initial}</div>
            <div className={styles.accountInfo}>
                <div className={styles.accountName}>{username}</div>
                <div className={styles.accountEmail}>{email}</div>
                <div className={styles.accountBadges}>
                    <Badge variant="human">Human</Badge>
                </div>
            </div>
            <button
                className={styles.homeNavRules}
                onClick={() => setShowRulesModal(true)}
                aria-label="How to play"
                title="How to play"
            >
                How to Play ?
            </button>
            <button className={homeStyles.homeNavJoin} onClick={() => setShowJoinModal(true)}> Join Game</button>
            <button className={homeStyles.homeNavPlay} onClick={handleCreateLobby}>▶ Create Game</button>
        </div>
    )
}

export default AccountHeader
