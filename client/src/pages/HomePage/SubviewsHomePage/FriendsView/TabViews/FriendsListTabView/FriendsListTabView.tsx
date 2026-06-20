import { useFriendsListTabView } from './useFriendsListTabView'
import InlineError from '../../../../../../components/InlineError/InlineError'
import { OnlineIndicator } from '../../../../../../components/OnlineIndicator/OnlineIndicator'
import './FriendsListTabView.css'

function FriendsListTabView() {
    const { friendsList, handleRemove, error } = useFriendsListTabView()

    return (
        <div className="friends-scroll">
            <InlineError message={error} />
            <div className="friends-grid">
                {friendsList.map((f) => (
                    <div key={f.friend.id} className="friend-item">
                        <div className="friend-avatar">
                            {(f.friend.username ?? '?')[0].toUpperCase()}
                            <OnlineIndicator userId={f.friend.id} />
                        </div>
                        <span className="friend-name">{f.friend.username}</span>
                        <button className="friend-remove" onClick={() => handleRemove(f.friend.id)}>Remove</button>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default FriendsListTabView
