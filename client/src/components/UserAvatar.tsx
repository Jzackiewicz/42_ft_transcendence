interface UserAvatarProps {
    username: string
    avatar?: string | null
    className?: string
}

function UserAvatar({ username, avatar, className = 'friend-avatar' }: UserAvatarProps) {
    if (avatar) {
        return <img src={avatar} alt={username} className={`${className} ${className}--img`} />
    }
    return <div className={className}>{username[0]?.toUpperCase() ?? '?'}</div>
}

export default UserAvatar
