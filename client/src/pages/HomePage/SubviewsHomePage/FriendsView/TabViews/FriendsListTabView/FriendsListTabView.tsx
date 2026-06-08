import { useFriendsListTabView } from './useFriendsListTabView'
import './FriendsListTabView.css'

function FriendsListTabView() {
    const { friendsList, handleRemove } = useFriendsListTabView()

    return (
        <div className="friends-scroll">
            <div className="friends-grid">
                {friendsList.map((f) => (
                    <div key={f.friend.id} className="friend-item">
                        <div className="friend-avatar">
                            {(f.friend.username ?? '?')[0].toUpperCase()}
                            {/* <span className={`friend-dot ${f.online ? 'online' : 'offline'}`} /> */}
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
