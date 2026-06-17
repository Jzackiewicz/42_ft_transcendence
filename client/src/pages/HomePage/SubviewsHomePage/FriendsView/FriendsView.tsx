import { useFriendsView } from './useFriendsView'
import FriendsListTabView from './TabViews/FriendsListTabView/FriendsListTabView'
import FriendsRequestTabView from './TabViews/FriendsRequestTabView/FriendsRequestTabView'
import FriendsFindTabView from './TabViews/FriendsFindTabView/FriendsFindTabView'
import './FriendsView.css'

function FriendsView() {
    const { activeTab, setActiveTab } = useFriendsView()

    return (
        <div className="section-card friends-view">
            <div className="section-title">👥 Friends</div>

            {/* ── Tabs ── */}
            <div className="friends-tabs">
                <button
                    className={`friends-tab ${activeTab === 'friends' ? 'active' : ''}`}
                    onClick={() => setActiveTab('friends')}
                >
                    Friends
                </button>
                <button
                    className={`friends-tab ${activeTab === 'requests' ? 'active' : ''}`}
                    onClick={() => setActiveTab('requests')}
                >
                    Requests
                </button>
                <button
                    className={`friends-tab ${activeTab === 'find' ? 'active' : ''}`}
                    onClick={() => setActiveTab('find')}
                >
                    Find Players
                </button>
            </div>

            {/* ── Content ── */}
            {activeTab === 'friends'  && <FriendsListTabView />}
            {activeTab === 'requests' && <FriendsRequestTabView />}
            {activeTab === 'find'     && <FriendsFindTabView />}
        </div>
    )
}

export default FriendsView
