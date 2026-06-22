import { useFriendsView } from './useFriendsView'
import FriendsListTabView from './TabViews/FriendsListTabView/FriendsListTabView'
import FriendsRequestTabView from './TabViews/FriendsRequestTabView/FriendsRequestTabView'
import FriendsFindTabView from './TabViews/FriendsFindTabView/FriendsFindTabView'
import { Card } from '../../../../components/Card/Card'
import { SectionTitle } from '../../../../components/SectionTitle/SectionTitle'
import { Icon } from '../../../../components/Icon/Icon'
import { cx } from '../../../../utils/cx'
import styles from './FriendsView.module.css'

function FriendsView() {
    const { activeTab, setActiveTab } = useFriendsView()

    return (
        <Card className={styles.friendsView}>
            <SectionTitle><Icon name="users" size="md" /> Friends</SectionTitle>

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
            {activeTab === 'find'     && <FriendsFindTabView />}
        </Card>
    )
}

export default FriendsView
