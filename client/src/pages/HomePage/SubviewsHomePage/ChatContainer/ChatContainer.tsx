import { useChatContainer } from './useChatContainer'
import './ChatContainer.css'

function ChatContainer() {
    const {  friendsList, activeConversation, activeId, setActiveId, handleChooseTab } = useChatContainer()

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
                                {/* <span className={`friend-dot ${f.online ? 'online' : 'offline'}`} /> */}
                            </div>
                            <span className="friend-name">{f.friend.username}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* ── Thread ── */}
            <div className="chat-thread">
                {/* <div className="chat-messages">
                    {active.messages.map(msg => (
                        <div key={msg.id} className={`chat-bubble-row ${msg.from}`}>
                            <div>
                                <div className="chat-bubble">{msg.text}</div>
                                <div className="chat-ts">{msg.timestamp}</div>
                            </div>
                        </div>
                    ))} */}
                {/* </div> */}

                {/* <div className="chat-input-row">
                    <input
                        className="chat-input"
                        placeholder={`Message ${active.username}…`}
                        value={draft}
                        onChange={e => setDraft(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleSend()}
                    />
                    <button className="chat-send-btn" onClick={handleSend}>Send</button>
                </div> */}
            </div>

        </div>
    )
}

export default ChatContainer
