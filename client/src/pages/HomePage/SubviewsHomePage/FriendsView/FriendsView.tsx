import { useFriendsView } from './useFriendsView'
import FriendsListTabView from './TabViews/FriendsListTabView/FriendsListTabView'
import FriendsRequestTabView from './TabViews/FriendsRequestTabView/FriendsRequestTabView'
import FriendsFindTabView from './TabViews/FriendsFindTabView/FriendsFindTabView'
import { Card } from '../../../../components/Card/Card'
import { SectionTitle } from '../../../../components/SectionTitle/SectionTitle'
import './FriendsView.css'

function FriendsView() {
    const { activeTab, setActiveTab } = useFriendsView()

    return (
        <Card className="friends-view">
            <SectionTitle>👥 Friends</SectionTitle>

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
        </Card>
    )
}

export default FriendsView
