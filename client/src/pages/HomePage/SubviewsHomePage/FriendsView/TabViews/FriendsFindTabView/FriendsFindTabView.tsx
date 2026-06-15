import { useFriendsFindTabView } from './useFriendsFindTabView'
import './FriendsFindTabView.css'

function FriendsFindTabView() {
    const { searchQuery, setSearchQuery, handleSendRequest, friends } = useFriendsFindTabView()

    return (
        <div className="friends-find">
            <div className="find-row">
                <input
                    className="find-input"
                    placeholder="Search by username…"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleSendRequest(searchQuery)}
                />
                <button className="find-btn" onClick={() => handleSendRequest(searchQuery)}>
                    Send Request
                </button>
            </div>
            <div className="friends-scroll">
                <div className="find-results">
                    {friends.map(user => (
                        <div key={user.id} className="find-result-item" onClick={() => setSearchQuery(user.username)}>
                            {user.username}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    )
}

export default FriendsFindTabView
