import { useChatContainer } from './useChatContainer'
import './ChatContainer.css'

function ChatContainer() {
    const { conversations, active, activeId, setActiveId, draft, setDraft, handleSend } = useChatContainer()

    return (
        <div className="chat-container">

            {/* ── Sidebar ── */}
            <div className="chat-sidebar">
                <div className="chat-sidebar-title">Messages</div>
                <div className="chat-conv-list">
                    {conversations.map(conv => (
                        <div
                            key={conv.id}
                            className={`chat-conv-item ${conv.id === activeId ? 'active' : ''}`}
                            onClick={() => setActiveId(conv.id)}
                        >
                            <div className="chat-conv-avatar" style={{ background: conv.color }}>
                                {conv.initial}
                            </div>
                            <div className="chat-conv-info">
                                <div className="chat-conv-name">{conv.username}</div>
                                <div className="chat-conv-last">{conv.lastMsg}</div>
                            </div>
                            {conv.unread > 0 && (
                                <div className="chat-unread">{conv.unread}</div>
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {/* ── Thread ── */}
            <div className="chat-thread">
                <div className="chat-messages">
                    {active.messages.map(msg => (
                        <div key={msg.id} className={`chat-bubble-row ${msg.from}`}>
                            <div>
                                <div className="chat-bubble">{msg.text}</div>
                                <div className="chat-ts">{msg.timestamp}</div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="chat-input-row">
                    <input
                        className="chat-input"
                        placeholder={`Message ${active.username}…`}
                        value={draft}
                        onChange={e => setDraft(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && handleSend()}
                    />
                    <button className="chat-send-btn" onClick={handleSend}>Send</button>
                </div>
            </div>

        </div>
    )
}

export default ChatContainer
