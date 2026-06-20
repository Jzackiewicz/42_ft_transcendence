import { useFriendsRequestTabView, FriendRequest } from './useFriendsRequestTabView'
import InlineError from '../../../../../../components/InlineError/InlineError'
import styles from './FriendsRequestTabView.module.css'
import shared from '../../FriendsView.module.css'

function FriendsRequestTabView() {
    const { incomingRequestsList, outgoingRequestsList,
            loading, error,
            handleAccept, handleDecline, handleCancel } = useFriendsRequestTabView()

    if (loading && incomingRequestsList.length === 0 && outgoingRequestsList.length === 0)
        return <span className={styles['friends-empty']}>Loading...</span>

    return (
        <div className={styles['friends-request-list']}>
            <InlineError message={error} />
            {incomingRequestsList.length === 0 && outgoingRequestsList.length === 0 && (
                <span className={styles['friends-empty']}>No pending requests</span>
            )}
            <div className={styles['request-types-container']}>
                <div className={styles['incoming-request']}>
                    {incomingRequestsList.map((r: FriendRequest) => (
                        <div key={r.id} className={styles['request-item']}>
                            <div className={shared['friend-avatar']}>{r.from_user.username[0].toUpperCase()}</div>
                            <span className={shared['friend-name']}>{r.from_user.username}</span>
                            <div className={styles['request-actions']}>
                                <button className={styles['req-accept']}  onClick={() => handleAccept(r.id)}>Accept</button>
                                <button className={styles['req-decline']} onClick={() => handleDecline(r.id)}>Decline</button>
                            </div>
                        </div>
                    ))}
                </div>
                <div className={styles['outgoing-request']}>
                    {outgoingRequestsList.map((r: FriendRequest) => (
                        <div key={r.id} className={styles['request-item']}>
                            <div className={shared['friend-avatar']}>{r.to_user.username[0].toUpperCase()}</div>
                            <span className={shared['friend-name']}>{r.to_user.username}</span>
                            <div className={styles['request-actions']}>
                                <button className={styles['req-decline']} onClick={() => handleCancel(r.id)}>Cancel</button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default FriendsRequestTabView
