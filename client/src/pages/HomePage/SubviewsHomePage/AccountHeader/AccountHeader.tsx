import './AccountHeader.css'

interface AccountHeaderProps {
    username: string
    email: string
    onLogout: () => void
}

function AccountHeader({ username, email, onLogout }: AccountHeaderProps) {
    const initial = username[0]?.toUpperCase() ?? '?'

    return (
        <div className="account-header">
            <div className="account-avatar">{initial}</div>
            <div className="account-info">
                <div className="account-name">{username}</div>
                <div className="account-email">{email}</div>
                <div className="account-badges">
                    <span className="badge human">Human</span>
                    <span className="badge joined">Player</span>
                </div>
            </div>
            <button className="home-nav-play" style={{ marginLeft: 'auto' }} onClick={onLogout}>
                Logout
            </button>
        </div>
    )
}

export default AccountHeader
