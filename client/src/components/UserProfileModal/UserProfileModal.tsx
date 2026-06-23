import { PublicUser } from '../../types/User'
import { useUserProfileModal } from './useUserProfileModal'
import { Modal } from '../Modal/Modal'
import { Avatar } from '../Avatar/Avatar'
import { StatsGrid, StatTile } from '../StatsGrid/StatsGrid'
import styles from './UserProfileModal.module.css'

interface UserProfileModalProps {
    user: PublicUser
    onClose: () => void
}

function UserProfileModal({ user, onClose }: UserProfileModalProps) {
    const { stats } = useUserProfileModal(user.id)

    const fmt = (val: number | undefined, suffix = '') =>
        stats === null ? '…' : `${val ?? 0}${suffix}`

    return (
        <Modal open onClose={onClose} contained>
            <div className={styles.header}>
                <Avatar name={user.username} imageUrl={user.avatar} size="lg" className={styles.profileAvatar} />
                <div className={styles.info}>
                    <div className={styles.username}>{user.username}</div>
                    <div className={styles.joined}>since {user.date_joined?.slice(0, 10)}</div>
                </div>
            </div>

            <StatsGrid>
                <StatTile value={fmt(stats?.games_played)} label="Games Played" color="cyan" />
                <StatTile value={fmt(stats?.wins)} label="Wins" color="magenta" />
                <StatTile value={fmt(stats?.win_rate, '%')} label="Win Rate" color="gold" />
                <StatTile value={fmt(stats?.avg_score)} label="Avg Score" color="green" />
                <StatTile value={fmt(stats?.correct_rate, '%')} label="Correct Rate" color="red" />
                <StatTile value={fmt(stats?.highest_score)} label="Best Score" color="violet" />
            </StatsGrid>
        </Modal>
    )
}

export default UserProfileModal
