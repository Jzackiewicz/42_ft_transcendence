import { useFriendsFindTabView } from './useFriendsFindTabView'
import { cx } from '../../../../../../utils/cx'
import styles from './FriendsFindTabView.module.css'
import shared from '../../FriendsView.module.css'

function FriendsFindTabView() {
    const { searchQuery, setSearchQuery, handleSendRequest, friends, status } = useFriendsFindTabView()

    return (
        <div>
            <div className={styles.findRow}>
                <input
                    className={styles.findInput}
                    placeholder="Search by username…"
                    value={searchQuery}
                    maxLength={40}
                    onChange={e => setSearchQuery(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSendRequest(searchQuery)}
                />
                <button className={styles.findBtn} onClick={() => handleSendRequest(searchQuery)}>
                    Send Request
                </button>
            </div>
            {status && (
                <span className={cx(styles.findStatus, styles[status.type === 'error' ? 'findStatusError' : 'findStatusSuccess'])}>
                    {status.message}
                </span>
            )}
            <div className={shared.friendsScroll}>
                <div className={styles.findResults}>
                    {friends.map(user => (
                        <div key={user.id} className={styles.findResultItem} onClick={() => setSearchQuery(user.username)}>
                            {user.username}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default FriendsFindTabView
