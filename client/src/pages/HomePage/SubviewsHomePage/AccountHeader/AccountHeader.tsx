import { User } from '../../../../types/User'
import { useAccountHeader } from './useAccountHeader'
import { Avatar } from '../../../../components/Avatar/Avatar'
import { Badge } from '../../../../components/Badge/Badge'
import { Button } from '../../../../components/Button/Button'
import { Icon } from '../../../../components/Icon/Icon'
import styles from './AccountHeader.module.css'

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

    let usernameField
    if (editingField === 'username') {
        usernameField = (
            <>
                <input
                    className={styles.accountEditInput}
                    value={editValue}
                    maxLength={40}
                    onChange={e => setEditValue(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') confirmEdit(); if (e.key === 'Escape') cancelEdit() }}
                    autoFocus
                />
                <button className={`${styles.editBtn} ${styles.confirmBtn}`} onClick={confirmEdit}>✓</button>
                <button className={`${styles.editBtn} ${styles.cancelBtn}`} onClick={cancelEdit}>✕</button>
            </>
        )
    } else {
        usernameField = (
            <>
                <div className={styles.accountName}>{user?.username}</div>
                <button className={styles.editBtn} onClick={() => startEdit('username')} title="Edit username">✎</button>
            </>
        )
    }

    let emailField
    if (editingField === 'email') {
        emailField = (
            <>
                <input
                    className={`${styles.accountEditInput} ${styles.accountEditInputSm}`}
                    value={editValue}
                    maxLength={254}
                    onChange={e => setEditValue(e.target.value)}
                    onKeyDown={e => { if (e.key === 'Enter') confirmEdit(); if (e.key === 'Escape') cancelEdit() }}
                    autoFocus
                />
                <button className={`${styles.editBtn} ${styles.confirmBtn}`} onClick={confirmEdit}>✓</button>
                <button className={`${styles.editBtn} ${styles.cancelBtn}`} onClick={cancelEdit}>✕</button>
            </>
        )
    } else {
        emailField = (
            <>
                <div className={styles.accountEmail}>{user?.email}</div>
                <button className={`${styles.editBtn} ${styles.editBtnSm}`} onClick={() => startEdit('email')} title="Edit email">✎</button>
            </>
        )
    }

    let errorMessage
    if (error) {
        errorMessage = <div className={styles.accountEditError}>{error}</div>
    }

    return (
        <div className={styles.accountHeader}>
            <div className={styles.accountAvatarWrapper}>
                <Avatar name={user?.username ?? ''} imageUrl={user?.avatar} size="lg" bg="accent" />
                <button className={`${styles.editBtn} ${styles.avatarEditBtn}`} onClick={handleAvatarClick} title="Change avatar">✎</button>
                <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    style={{ display: 'none' }}
                    onChange={handleAvatarChange}
                />
            </div>

            <div className={styles.accountInfo}>
                <div className={styles.accountFieldRow}>{usernameField}</div>
                <div className={styles.accountFieldRow}>{emailField}</div>
                {errorMessage}
                <div className={styles.accountBadges}>
                    <Badge variant="joined">since: {user?.date_joined?.slice(0, 10)}</Badge>
                </div>
            </div>

            <Button variant="ghost" onClick={() => setShowRulesModal(true)} aria-label="How to play" title="How to play">
                How to Play ?
            </Button>
            <Button variant="secondary" onClick={() => setShowJoinModal(true)}><Icon name="enter" size="sm" /> Join Game</Button>
            <Button onClick={handleCreateLobby}><Icon name="play" size="sm" /> Create Game</Button>
        </div>
    )
}

export default AccountHeader
