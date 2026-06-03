import { useFriendsRequestTabView, FriendRequest } from './useFriendsRequestTabView'
import './FriendsRequestTabView.css'

function FriendsRequestTabView() {
    const { requests, handleAccept, handleDecline } = useFriendsRequestTabView()

    return (
        <div className="friends-scroll">
            <div className="friends-request-list">
                {requests.length === 0 && (
                    <span className="friends-empty">No pending requests</span>
                )}
                {requests.map((r: FriendRequest) => (
                    <div key={r.id} className="request-item">
                        <div className="friend-avatar">{r.username[0].toUpperCase()}</div>
                        <span className="friend-name">{r.username}</span>
                        <div className="request-actions">
                            <button className="req-accept"  onClick={() => handleAccept(r.id)}>Accept</button>
                            <button className="req-decline" onClick={() => handleDecline(r.id)}>Decline</button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default FriendsRequestTabView
