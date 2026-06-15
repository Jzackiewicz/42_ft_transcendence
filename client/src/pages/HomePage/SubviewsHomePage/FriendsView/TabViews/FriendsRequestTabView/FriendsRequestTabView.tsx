import { useFriendsRequestTabView, FriendRequest } from './useFriendsRequestTabView'
import './FriendsRequestTabView.css'

function FriendsRequestTabView() {
    const { incomingRequestsList, outgoingRequestsList,
            loading,
            handleAccept, handleDecline, handleCancel } = useFriendsRequestTabView()

    if (loading) 
        return <span className="friends-empty">Loading...</span>

    return (
        <div className="friends-request-list">
            {incomingRequestsList.length === 0 && outgoingRequestsList.length === 0 && (
                <span className="friends-empty">No pending requests</span>
            )}
            <div className="request-types-container">
                <div className="incoming-request">
                    {incomingRequestsList.map((r: FriendRequest) => (
                        <div key={r.id} className="request-item">
                            <div className="friend-avatar">{r.from_user.username[0].toUpperCase()}</div>
                            <span className="friend-name">{r.from_user.username}</span>
                            <div className="request-actions">
                                <button className="req-accept"  onClick={() => handleAccept(r.id)}>Accept</button>
                                <button className="req-decline" onClick={() => handleDecline(r.id)}>Decline</button>
                            </div>
                        </div>
                    ))}
                </div>
                <div className="outgoing-request">
                    {outgoingRequestsList.map((r: FriendRequest) => (
                        <div key={r.id} className="request-item">
                            <div className="friend-avatar">{r.to_user.username[0].toUpperCase()}</div>
                            <span className="friend-name">{r.to_user.username}</span>
                            <div className="request-actions">
                                <button className="req-decline" onClick={() => handleCancel(r.id)}>Cancel</button>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default FriendsRequestTabView
