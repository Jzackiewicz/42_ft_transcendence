import { OnlineIndicator } from './OnlineIndicator/OnlineIndicator'
import styles from './UserAvatar.module.css'

interface UserAvatarProps {
    username: string
    avatar?: string | null
    userId?: number
}

function UserAvatar({ username, avatar, userId }: UserAvatarProps) {
    return (
        <div className={styles.wrapper}>
            <div className={styles.avatar}>
                {avatar
                    ? <img src={avatar} alt={username} className={styles.avatarImg} />
                    : username[0]?.toUpperCase() ?? '?'
                }
            </div>
            {userId !== undefined && <OnlineIndicator userId={userId} />}
        </div>
    )
}

export default UserAvatar
