import { useFriendsRequestTabView, FriendRequest } from './useFriendsRequestTabView'
import { PublicUser } from '../../../../../../types/User'
import InlineError from '../../../../../../components/InlineError/InlineError'
import { Avatar } from '../../../../../../components/Avatar/Avatar'
import { Button } from '../../../../../../components/Button/Button'
import styles from './FriendsRequestTabView.module.css'
import shared from '../../FriendsView.module.css'

interface FriendsRequestTabViewProps {
    onOpenProfile: (user: PublicUser) => void
}

function FriendsRequestTabView({ onOpenProfile }: FriendsRequestTabViewProps) {
    const { incomingRequestsList, outgoingRequestsList,
            loading, error,
            handleAccept, handleDecline, handleCancel } = useFriendsRequestTabView()

    if (loading && incomingRequestsList.length === 0 && outgoingRequestsList.length === 0)
        return <span className={styles.friendsEmpty}>Loading...</span>

    return (
        <div className={styles.friendsRequestList}>
            <InlineError message={error} />
            {incomingRequestsList.length === 0 && outgoingRequestsList.length === 0 && (
                <span className={styles.friendsEmpty}>No pending requests</span>
            )}
            <div className={styles.requestTypesContainer}>
                <div className={styles.incomingRequest}>
                    {incomingRequestsList.map((r: FriendRequest) => (
                        <div key={r.id} className={styles.requestItem}>
                            <Avatar name={r.from_user.username} imageUrl={r.from_user.avatar} size="md" onClick={() => onOpenProfile(r.from_user)} />
                            <span className={shared.friendName} title={r.from_user.username}>{r.from_user.username}</span>
                            <div className={styles.requestActions}>
                                <Button variant="primary" size="sm" onClick={() => handleAccept(r.id)}>Accept</Button>
                                <Button variant="ghost" size="sm" onClick={() => handleDecline(r.id)}>Decline</Button>
                            </div>
                        </div>
                    ))}
                </div>
                <div className={styles.outgoingRequest}>
                    {outgoingRequestsList.map((r: FriendRequest) => (
                        <div key={r.id} className={styles.requestItem}>
                            <Avatar name={r.to_user.username} imageUrl={r.to_user.avatar} size="md" onClick={() => onOpenProfile(r.to_user)} />
                            <span className={shared.friendName} title={r.to_user.username}>{r.to_user.username}</span>
                            <div className={styles.requestActions}>
                                <Button variant="ghost" size="sm" onClick={() => handleCancel(r.id)}>Cancel</Button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default FriendsRequestTabView
