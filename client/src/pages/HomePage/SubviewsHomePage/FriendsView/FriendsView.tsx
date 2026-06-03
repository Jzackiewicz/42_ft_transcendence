import { useFriendsView } from './useFriendsView'
import './FriendsView.css'

function FriendsView() {
    const {
        activeTab, setActiveTab,
        friends, requests,
        searchQuery, setSearchQuery,
        handleRemove, handleAccept, handleDecline, handleSendRequest,
    } = useFriendsView()

    return (
        <div className="section-card friends-view">
            <div className="section-title">👥 Friends</div>

            {/* ── Tabs ── */}
            <div className="friends-tabs">
                <button
                    className={`friends-tab ${activeTab === 'friends' ? 'active' : ''}`}
                    onClick={() => setActiveTab('friends')}
                    // style={{ background: 'red' }}
                >
                    Friends
                    {/* {friends.length > 0 && <span className="tab-badge">{friends.length}</span>} */}
                </button>
                <button
                    className={`friends-tab ${activeTab === 'requests' ? 'active' : ''}`}
                    onClick={() => setActiveTab('requests')}
                >
                    Requests
                    {requests.length > 0 && <span className="tab-badge tab-badge--alert">{requests.length}</span>}
                </button>
                <button
                    className={`friends-tab ${activeTab === 'find' ? 'active' : ''}`}
                    onClick={() => setActiveTab('find')}
                >
                    Find Players
                </button>
            </div>

            {/* ── Friends list ── */}
            {activeTab === 'friends' && (
                <div className="friends-scroll">
                    <div className="friends-grid">
                        {friends.map(f => (
                            <div key={f.id} className="friend-item">
                                <div className="friend-avatar">
                                    {f.username[0].toUpperCase()}
                                    <span className={`friend-dot ${f.online ? 'online' : 'offline'}`} />
                                </div>
                                <span className="friend-name">{f.username}</span>
                                <button className="friend-remove" onClick={() => handleRemove(f.id)}>Remove</button>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* ── Requests list ── */}
            {activeTab === 'requests' && (
                <div className="friends-scroll">
                    <div className="friends-request-list">
                        {requests.length === 0 && (
                            <span className="friends-empty">No pending requests</span>
                        )}
                        {requests.map(r => (
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
            )}

            {/* ── Find players ── */}
            {activeTab === 'find' && (
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
                </div>
            )}
        </div>
    )
}

export default FriendsView
