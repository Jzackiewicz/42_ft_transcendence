import { useFriendsListTabView } from './useFriendsListTabView'
import { PublicUser } from '../../../../../../types/User'
import InlineError from '../../../../../../components/InlineError/InlineError'
import { Avatar } from '../../../../../../components/Avatar/Avatar'
import { Button } from '../../../../../../components/Button/Button'
import styles from './FriendsListTabView.module.css'
import shared from '../../FriendsView.module.css'

interface FriendsListTabViewProps {
    onOpenProfile: (user: PublicUser) => void
}

function FriendsListTabView({ onOpenProfile }: FriendsListTabViewProps) {
    const { friendsList, handleRemove, error } = useFriendsListTabView()

    return (
        <div className={shared.friendsScroll}>
            <InlineError message={error} />
            <div className={styles.friendsGrid}>
                {friendsList.map((f) => (
                    <div key={f.friend.id} className={styles.friendItem}>
                        <Avatar name={f.friend.username} imageUrl={f.friend.avatar} size="md" userId={f.friend.id} onClick={() => onOpenProfile(f.friend)} />
                        <span className={shared.friendName} title={f.friend.username}>{f.friend.username}</span>
                        <Button variant="ghost" size="sm" onClick={() => handleRemove(f.friend.id)}>Remove</Button>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default FriendsListTabView
