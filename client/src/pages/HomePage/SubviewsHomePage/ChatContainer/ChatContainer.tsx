import { useChatContainer } from './useChatContainer'
import './ChatContainer.css'

function ChatContainer() {
    const { friendsList, activeId, messages, myUsername, handleChooseTab } = useChatContainer()

    return (
        <div className="chat-container">

            {/* ── Sidebar ── */}
            <div className="chat-sidebar">
                <div className="chat-sidebar-title">Messages</div>
                <div className="chat-conv-list">
                    {friendsList.map((f) => (
                        <div key={f.friend.id} className={`friend-item ${f.friend.id === activeId ? 'active' : ''}`} onClick={() => handleChooseTab(f.friend.id)}>
                            <div className="friend-avatar">
                                {(f.friend.username ?? '?')[0].toUpperCase()}
                            </div>
                            <span className="friend-name">{f.friend.username}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* ── Thread ── */}
            <div className="chat-thread">
                <div className="chat-messages">
                    {messages.map((msg, i) => (
                        <div key={i} className={`chat-bubble-row ${msg.sender_username === myUsername ? 'me' : 'them'}`}>
                            <div className="chat-bubble">{msg.message}</div>
                            <div className="chat-ts">{msg.timestamp}</div>
                        </div>
                    ))}
                </div>
            </div>

        </div>
    )
}

export default ChatContainer
