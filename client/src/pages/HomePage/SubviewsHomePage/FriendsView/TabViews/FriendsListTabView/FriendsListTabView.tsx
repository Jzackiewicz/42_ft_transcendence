import { useFriendsListTabView, Friend } from './useFriendsListTabView'
import './FriendsListTabView.css'

function FriendsListTabView() {
    const { friends, handleRemove } = useFriendsListTabView()

    return (
        <div className="friends-scroll">
            <div className="friends-grid">
                {friends.map((f: Friend) => (
                    <div key={f.id} className="friend-item">
                        <div className="friend-avatar">
                            {f.username[0].toUpperCase()}
                            <span className={`friend-dot ${f.online ? 'online' : 'offline'}`} />
                        </div>
                        <span className="friend-name">{f.username}</span>
                        <button className="friend-remove" onClick={() => handleRemove(f.id)}>Remove</button>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default FriendsListTabView
