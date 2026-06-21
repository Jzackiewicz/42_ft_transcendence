import { useFriendsFindTabView } from './useFriendsFindTabView'
import { cx } from '../../../../../../utils/cx'
import { Button } from '../../../../../../components/Button/Button'
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
                    onChange={e => setSearchQuery(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSendRequest(searchQuery)}
                />
                <Button onClick={() => handleSendRequest(searchQuery)}>
                    Send Request
                </Button>
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
