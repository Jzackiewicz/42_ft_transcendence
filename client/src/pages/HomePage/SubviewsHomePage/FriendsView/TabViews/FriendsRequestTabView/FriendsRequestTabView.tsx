import { useFriendsRequestTabView, FriendRequest } from './useFriendsRequestTabView'
import InlineError from '../../../../../../components/InlineError/InlineError'
import styles from './FriendsRequestTabView.module.css'
import shared from '../../FriendsView.module.css'

function FriendsRequestTabView() {
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
                            <div className={shared.friendAvatar}>{r.from_user.username[0].toUpperCase()}</div>
                            <span className={shared.friendName}>{r.from_user.username}</span>
                            <div className={styles.requestActions}>
                                <button className={styles.reqAccept}  onClick={() => handleAccept(r.id)}>Accept</button>
                                <button className={styles.reqDecline} onClick={() => handleDecline(r.id)}>Decline</button>
                            </div>
                        </div>
                    ))}
                </div>
                <div className={styles.outgoingRequest}>
                    {outgoingRequestsList.map((r: FriendRequest) => (
                        <div key={r.id} className={styles.requestItem}>
                            <div className={shared.friendAvatar}>{r.to_user.username[0].toUpperCase()}</div>
                            <span className={shared.friendName}>{r.to_user.username}</span>
                            <div className={styles.requestActions}>
                                <button className={styles.reqDecline} onClick={() => handleCancel(r.id)}>Cancel</button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default FriendsRequestTabView
