import { useFriendsFindTabView } from './useFriendsFindTabView'
import { PublicUser } from '../../../../../../types/User'
import { cx } from '../../../../../../utils/cx'
import UserAvatar from '../../../../../../components/UserAvatar'
import styles from './FriendsFindTabView.module.css'
import shared from '../../FriendsView.module.css'

interface FriendsFindTabViewProps {
    onSelectUser: (user: PublicUser) => void
}

function FriendsFindTabView({ onSelectUser }: FriendsFindTabViewProps) {
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
                        <div key={user.id} className={styles.findResultItem} onClick={() => onSelectUser(user)}>
                            <UserAvatar username={user.username} avatar={user.avatar} />
                            <span className={shared.friendName}>{user.username}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default FriendsFindTabView
