import { Badge } from '../../../../components/Badge/Badge'
import { Button } from '../../../../components/Button/Button'
import styles from './AccountHeader.module.css'

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
            <Button
                variant="ghost"
                onClick={() => setShowRulesModal(true)}
                aria-label="How to play"
                title="How to play"
            >
                How to Play ?
            </Button>
            <Button variant="secondary" onClick={() => setShowJoinModal(true)}> Join Game</Button>
            <Button onClick={handleCreateLobby}>▶ Play Now</Button>
        </div>
    )
}

export default AccountHeader
