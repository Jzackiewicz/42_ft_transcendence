import { useFriendsFindTabView } from './useFriendsFindTabView'
import { cx } from '../../../../../../utils/cx'
import styles from './FriendsFindTabView.module.css'
import shared from '../../FriendsView.module.css'

function FriendsFindTabView() {
    const { searchQuery, setSearchQuery, handleSendRequest, friends, status } = useFriendsFindTabView()

    return (
        <div className={styles['friends-find']}>
            <div className={styles['find-row']}>
                <input
                    className={styles['find-input']}
                    placeholder="Search by username…"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSendRequest(searchQuery)}
                />
                <button className={styles['find-btn']} onClick={() => handleSendRequest(searchQuery)}>
                    Send Request
                </button>
            </div>
            {status && (
                <span className={cx(styles['find-status'], styles[`find-status--${status.type}`])}>
                    {status.message}
                </span>
            )}
            <div className={shared['friends-scroll']}>
                <div className={styles['find-results']}>
                    {friends.map(user => (
                        <div key={user.id} className={styles['find-result-item']} onClick={() => setSearchQuery(user.username)}>
                            {user.username}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default FriendsFindTabView
