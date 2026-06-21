import { useFriendsListTabView } from './useFriendsListTabView'
import InlineError from '../../../../../../components/InlineError/InlineError'
import { OnlineIndicator } from '../../../../../../components/OnlineIndicator/OnlineIndicator'
import styles from './FriendsListTabView.module.css'
import shared from '../../FriendsView.module.css'

function FriendsListTabView() {
    const { friendsList, handleRemove, error } = useFriendsListTabView()

    return (
        <div className={shared.friendsScroll}>
            <InlineError message={error} />
            <div className={styles.friendsGrid}>
                {friendsList.map((f) => (
                    <div key={f.friend.id} className={styles.friendItem}>
                        <div className={shared.friendAvatar}>
                            {(f.friend.username ?? '?')[0].toUpperCase()}
                        </div>
                        <OnlineIndicator userId={f.friend.id} />
                        <span className={shared.friendName}>{f.friend.username}</span>
                        <button className={styles.friendRemove} onClick={() => handleRemove(f.friend.id)}>Remove</button>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default FriendsListTabView
