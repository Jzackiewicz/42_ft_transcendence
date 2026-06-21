import { useFriendsView } from './useFriendsView'
import FriendsListTabView from './TabViews/FriendsListTabView/FriendsListTabView'
import FriendsRequestTabView from './TabViews/FriendsRequestTabView/FriendsRequestTabView'
import FriendsFindTabView from './TabViews/FriendsFindTabView/FriendsFindTabView'
import { PublicUser } from '../../../../types/User'
import { Card } from '../../../../components/Card/Card'
import { SectionTitle } from '../../../../components/SectionTitle/SectionTitle'
import { cx } from '../../../../utils/cx'
import styles from './FriendsView.module.css'

interface FriendsViewProps {
    onSelectUser: (user: PublicUser) => void
}

function FriendsView({ onSelectUser }: FriendsViewProps) {
    const { activeTab, setActiveTab } = useFriendsView()

    return (
        <Card className={styles.friendsView}>
            <SectionTitle>👥 Friends</SectionTitle>

            {/* ── Tabs ── */}
            <div className={styles.friendsTabs}>
                <button
                    className={cx(styles.friendsTab, activeTab === 'friends' && styles.active)}
                    onClick={() => setActiveTab('friends')}
                >
                    Friends
                </button>
                <button
                    className={cx(styles.friendsTab, activeTab === 'requests' && styles.active)}
                    onClick={() => setActiveTab('requests')}
                >
                    Requests
                </button>
                <button
                    className={cx(styles.friendsTab, activeTab === 'find' && styles.active)}
                    onClick={() => setActiveTab('find')}
                >
                    Find Players
                </button>
            </div>

            {/* ── Content ── */}
            {activeTab === 'friends'  && <FriendsListTabView />}
            {activeTab === 'requests' && <FriendsRequestTabView />}
            {activeTab === 'find'     && <FriendsFindTabView onSelectUser={onSelectUser} />}
        </Card>
    )
}

export default FriendsView
