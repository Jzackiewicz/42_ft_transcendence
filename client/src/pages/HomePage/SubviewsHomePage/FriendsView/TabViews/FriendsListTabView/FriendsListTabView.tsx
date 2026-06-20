import { useFriendsListTabView } from './useFriendsListTabView'
import InlineError from '../../../../../../components/InlineError/InlineError'
import { OnlineIndicator } from '../../../../../../components/OnlineIndicator/OnlineIndicator'
import styles from './FriendsListTabView.module.css'
import shared from '../../FriendsView.module.css'

function FriendsListTabView() {
    const { friendsList, handleRemove, error } = useFriendsListTabView()

    return (
        <div className={shared['friends-scroll']}>
            <InlineError message={error} />
            <div className={styles['friends-grid']}>
                {friendsList.map((f) => (
                    <div key={f.friend.id} className={styles['friend-item']}>
                        <div className={shared['friend-avatar']}>
                            {(f.friend.username ?? '?')[0].toUpperCase()}
                        </div>
                        <OnlineIndicator userId={f.friend.id} />
                        <span className={shared['friend-name']}>{f.friend.username}</span>
                        <button className={styles['friend-remove']} onClick={() => handleRemove(f.friend.id)}>Remove</button>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default FriendsListTabView
