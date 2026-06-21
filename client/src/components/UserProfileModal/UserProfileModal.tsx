import { PublicUser } from '../../types/User'
import styles from './UserProfileModal.module.css'

interface UserProfileModalProps {
    user: PublicUser
    onClose: () => void
}

function UserProfileModal({ user, onClose }: UserProfileModalProps) {
    return (
        <div className={styles.overlay} onClick={onClose} role="dialog" aria-modal="true">
            <div className={styles.modal} onClick={e => e.stopPropagation()}>
                <button className={styles.closeBtn} onClick={onClose} aria-label="Close">×</button>

                <div className={styles.header}>
                    <div className={styles.avatar}>
                        {user.avatar
                            ? <img src={user.avatar} alt={user.username} className={styles.avatarImg} />
                            : user.username[0]?.toUpperCase()
                        }
                    </div>
                    <div className={styles.info}>
                        <div className={styles.username}>{user.username}</div>
                        <div className={styles.joined}>since {user.date_joined?.slice(0, 10)}</div>
                    </div>
                </div>

                <div className={styles.stats}>
                    <div className={styles.statCard}>
                        <span className={styles.statLabel}>Games Played</span>
                        <span className={styles.statValue}>—</span>
                    </div>
                    <div className={styles.statCard}>
                        <span className={styles.statLabel}>Wins</span>
                        <span className={styles.statValue}>—</span>
                    </div>
                    <div className={styles.statCard}>
                        <span className={styles.statLabel}>Best Score</span>
                        <span className={styles.statValue}>—</span>
                    </div>
                    <div className={styles.statCard}>
                        <span className={styles.statLabel}>Win Rate</span>
                        <span className={styles.statValue}>—</span>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default UserProfileModal
