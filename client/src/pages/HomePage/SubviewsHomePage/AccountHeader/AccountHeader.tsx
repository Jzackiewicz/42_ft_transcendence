import './AccountHeader.css'

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
        <div className="account-header">
            <div className="account-avatar">{initial}</div>
            <div className="account-info">
                <div className="account-name">{username}</div>
                <div className="account-email">{email}</div>
                <div className="account-badges">
                    <span className="badge human">Human</span>
                </div>
            </div>
            <button
                className="home-nav-rules"
                onClick={() => setShowRulesModal(true)}
                aria-label="How to play"
                title="How to play"
            >
                How to Play ?
            </button>
            <button className="home-nav-join" onClick={() => setShowJoinModal(true)}> Join Game</button>
            <button className="home-nav-play" onClick={handleCreateLobby}>▶ Play Now</button>
        </div>
    )
}

export default AccountHeader
