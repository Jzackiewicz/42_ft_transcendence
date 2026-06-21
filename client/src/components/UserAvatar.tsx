import { OnlineIndicator } from './OnlineIndicator'

interface UserAvatarProps {
    username: string
    avatar?: string | null
    userId?: number
    className?: string
}

function UserAvatar({ username, avatar, userId, className = 'friend-avatar' }: UserAvatarProps) {
    return (
        <div className={className}>
            {avatar
                ? <img src={avatar} alt={username} className={`${className}-img`} />
                : username[0]?.toUpperCase() ?? '?'
            }
            {userId !== undefined && <OnlineIndicator userId={userId} />}
        </div>
    )
}

export default UserAvatar
