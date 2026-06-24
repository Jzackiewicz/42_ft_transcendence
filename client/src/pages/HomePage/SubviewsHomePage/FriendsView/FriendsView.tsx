import { useState } from 'react'
import { useFriendsView } from './useFriendsView'
import FriendsListTabView from './TabViews/FriendsListTabView/FriendsListTabView'
import FriendsRequestTabView from './TabViews/FriendsRequestTabView/FriendsRequestTabView'
import FriendsFindTabView from './TabViews/FriendsFindTabView/FriendsFindTabView'
import { PublicUser } from '../../../../types/User'
import { Card } from '../../../../components/Card/Card'
import { SectionTitle } from '../../../../components/SectionTitle/SectionTitle'
import { Icon } from '../../../../components/Icon/Icon'
import UserProfileModal from '../../../../components/UserProfileModal/UserProfileModal'
import { cx } from '../../../../utils/cx'
import styles from './FriendsView.module.css'

function FriendsView() {
    const { activeTab, setActiveTab } = useFriendsView()
    const [selectedUser, setSelectedUser] = useState<PublicUser | null>(null)

    return (
        <>
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
            {activeTab === 'friends'  && <FriendsListTabView onOpenProfile={setSelectedUser} />}
            {activeTab === 'requests' && <FriendsRequestTabView onOpenProfile={setSelectedUser} />}
            {activeTab === 'find'     && <FriendsFindTabView onOpenProfile={setSelectedUser} />}
        </Card>

        {selectedUser && (
            <UserProfileModal user={selectedUser} onClose={() => setSelectedUser(null)} />
        )}
        </>
    )
}

export default FriendsView
