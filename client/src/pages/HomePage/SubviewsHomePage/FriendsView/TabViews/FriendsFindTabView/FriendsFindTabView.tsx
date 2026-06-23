import { useFriendsFindTabView } from './useFriendsFindTabView'
import { PublicUser } from '../../../../../../types/User'
import { cx } from '../../../../../../utils/cx'
import { Avatar } from '../../../../../../components/Avatar/Avatar'
import { Button } from '../../../../../../components/Button/Button'
import styles from './FriendsFindTabView.module.css'
import shared from '../../FriendsView.module.css'

interface FriendsFindTabViewProps {
    onOpenProfile: (user: PublicUser) => void
}

function FriendsFindTabView({ onOpenProfile }: FriendsFindTabViewProps) {
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
                            <Avatar
                                name={user.username}
                                imageUrl={user.avatar}
                                size="md"
                                userId={user.id}
                                onClick={e => { e.stopPropagation(); onOpenProfile(user) }}
                            />
                            <span className={shared.friendName}>{user.username}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default FriendsFindTabView
