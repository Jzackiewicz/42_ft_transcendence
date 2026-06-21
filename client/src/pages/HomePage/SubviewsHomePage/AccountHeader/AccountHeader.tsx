import { useState, useEffect } from 'react'
import { User } from '../../../../types/User'
import { useAccountHeader } from './useAccountHeader'
import './AccountHeader.css'

interface AccountHeaderProps {
    user: User | null | undefined
    setUser: (u: User | null) => void
    setShowJoinModal: (bool: boolean) => void
    setShowRulesModal: (bool: boolean) => void
    handleCreateLobby: () => void
}

function AccountHeader({ user, setUser, setShowJoinModal, setShowRulesModal, handleCreateLobby }: AccountHeaderProps) {
    const {
        editingField, editValue, setEditValue, error,
        startEdit, cancelEdit, confirmEdit,
        fileInputRef, handleAvatarClick, handleAvatarChange,
    } = useAccountHeader(user, setUser)

    const initial = user?.username?.[0]?.toUpperCase() ?? '?'
    const [avatarBroken, setAvatarBroken] = useState(false)

    useEffect(() => {
        setAvatarBroken(false)
    }, [user?.avatar])

    let avatarContent
    if (user?.avatar && !avatarBroken) {
        avatarContent = (
            <img
                src={user.avatar}
                alt="avatar"
                className="account-avatar-img"
                onError={() => setAvatarBroken(true)}
            />
        )
    } else {
        avatarContent = initial
    }

    let usernameField
    if (editingField === 'username') {
        usernameField = (
            <>
                <input
                    className="account-edit-input"
                    value={editValue}
                    onChange={e => setEditValue(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') confirmEdit(); if (e.key === 'Escape') cancelEdit() }}
                    autoFocus
                />
                <button className="edit-btn confirm-btn" onClick={confirmEdit}>✓</button>
                <button className="edit-btn cancel-btn" onClick={cancelEdit}>✕</button>
            </>
        )
    } else {
        usernameField = (
            <>
                <div className="account-name">{user?.username}</div>
                <button className="edit-btn" onClick={() => startEdit('username')} title="Edit username">✎</button>
            </>
        )
    }

    let emailField
    if (editingField === 'email') {
        emailField = (
            <>
                <input
                    className="account-edit-input account-edit-input--sm"
                    value={editValue}
                    onChange={e => setEditValue(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') confirmEdit(); if (e.key === 'Escape') cancelEdit() }}
                    autoFocus
                />
                <button className="edit-btn confirm-btn" onClick={confirmEdit}>✓</button>
                <button className="edit-btn cancel-btn" onClick={cancelEdit}>✕</button>
            </>
        )
    } else {
        emailField = (
            <>
                <div className="account-email">{user?.email}</div>
                <button className="edit-btn edit-btn--sm" onClick={() => startEdit('email')} title="Edit email">✎</button>
            </>
        )
    }

    let errorMessage
    if (error) {
        errorMessage = <div className="account-edit-error">{error}</div>
    }

    return (
        <div className="account-header">
            <div className="account-avatar-wrapper">
                <div className="account-avatar">{avatarContent}</div>
                <button className="edit-btn avatar-edit-btn" onClick={handleAvatarClick} title="Change avatar">✎</button>
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    style={{ display: 'none' }}
                    onChange={handleAvatarChange}
                />
            </div>

            <div className="account-info">
                <div className="account-field-row">{usernameField}</div>
                <div className="account-field-row">{emailField}</div>
                {errorMessage}
                <div className="account-badges">
                    <span className="badge human">{user?.date_joined?.slice(0, 10)}</span>
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
            <button className="home-nav-join" onClick={() => setShowJoinModal(true)}>Join Game</button>
            <button className="home-nav-play" onClick={handleCreateLobby}>▶ Play Now</button>
        </div>
    )
}

export default AccountHeader
