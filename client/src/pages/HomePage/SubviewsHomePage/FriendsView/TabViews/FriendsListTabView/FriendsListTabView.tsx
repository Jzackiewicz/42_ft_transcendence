import { useFriendsListTabView } from './useFriendsListTabView'
import InlineError from '../../../../../../components/InlineError'
import UserAvatar from '../../../../../../components/UserAvatar'
import { OnlineIndicator } from '../../../../../../components/OnlineIndicator'
import './FriendsListTabView.css'

function FriendsListTabView() {
    const { friendsList, handleRemove, error } = useFriendsListTabView()

    return (
        <div className="friends-scroll">
            <InlineError message={error} />
            <div className="friends-grid">
                {friendsList.map((f) => (
                    <div key={f.friend.id} className="friend-item">
                        <UserAvatar username={f.friend.username} avatar={f.friend.avatar} />
                        <OnlineIndicator userId={f.friend.id} />
                        <span className="friend-name">{f.friend.username}</span>
                        <button className="friend-remove" onClick={() => handleRemove(f.friend.id)}>Remove</button>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default FriendsListTabView
