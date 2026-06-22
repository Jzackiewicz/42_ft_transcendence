import { Badge } from '../../../../components/Badge/Badge'
import { Button } from '../../../../components/Button/Button'
import { Avatar } from '../../../../components/Avatar/Avatar'
import { Icon } from '../../../../components/Icon/Icon'
import styles from './AccountHeader.module.css'

interface AccountHeaderProps {
    username: string
    email: string
    setShowJoinModal: (bool: boolean) => void
    setShowRulesModal: (bool: boolean) => void
    handleCreateLobby: () => void
}

function AccountHeader({ username, email, setShowJoinModal, setShowRulesModal, handleCreateLobby }: AccountHeaderProps) {
    return (
        <div className={styles.accountHeader}>
            <Avatar name={username} size="lg" bg="cyan" />
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
            <Button variant="secondary" onClick={() => setShowJoinModal(true)}><Icon name="enter" size="sm" /> Join Game</Button>
            <Button onClick={handleCreateLobby}><Icon name="play" size="sm" /> Play Now</Button>
        </div>
    )
}

export default AccountHeader
