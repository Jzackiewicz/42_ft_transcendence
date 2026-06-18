import { useFriendsRequestTabView, FriendRequest } from './useFriendsRequestTabView'
import InlineError from '../../../../../../components/InlineError'
import UserAvatar from '../../../../../../components/UserAvatar'
import './FriendsRequestTabView.css'

function FriendsRequestTabView() {
    const { incomingRequestsList, outgoingRequestsList,
            loading, error,
            handleAccept, handleDecline, handleCancel } = useFriendsRequestTabView()

    if (loading && incomingRequestsList.length === 0 && outgoingRequestsList.length === 0)
        return <span className="friends-empty">Loading...</span>

    let requestsContent
    if (incomingRequestsList.length === 0 && outgoingRequestsList.length === 0) {
        requestsContent = <span className="friends-empty">No pending requests</span>
    } else {
        const incoming = incomingRequestsList.map((r: FriendRequest) => (
            <div key={r.id} className="request-item">
                <UserAvatar username={r.from_user.username} avatar={r.from_user.avatar} />
                <span className="friend-name">{r.from_user.username}</span>
                <div className="request-actions">
                    <button className="req-accept"  onClick={() => handleAccept(r.id)}>Accept</button>
                    <button className="req-decline" onClick={() => handleDecline(r.id)}>Decline</button>
                </div>
            </div>
        ))

        const outgoing = outgoingRequestsList.map((r: FriendRequest) => (
            <div key={r.id} className="request-item">
                <UserAvatar username={r.to_user.username} avatar={r.to_user.avatar} />
                <span className="friend-name">{r.to_user.username}</span>
                <div className="request-actions">
                    <button className="req-decline" onClick={() => handleCancel(r.id)}>Cancel</button>
                </div>
            </div>
        ))

        requestsContent = (
            <div className="request-types-container">
                <div className="incoming-request">{incoming}</div>
                <div className="outgoing-request">{outgoing}</div>
            </div>
        )
    }

    return (
        <div className="friends-request-list">
            <InlineError message={error} />
            {requestsContent}
        </div>
    )
}

export default FriendsRequestTabView
