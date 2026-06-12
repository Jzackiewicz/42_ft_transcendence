import { useState } from 'react'
import { useChatContainer } from './useChatContainer'
import './ChatContainer.css'

function ChatContainer() {
    const { friendsList, activeId, messages, myUsername, handleChooseTab, handleSend } = useChatContainer()
    const [draft, setDraft] = useState('')

    const send = () => {
        handleSend(draft)
        setDraft('')
    }

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
                    {messages.filter(msg => msg.message).map((msg, i) => (
                        <div key={i} className={`chat-bubble-row ${msg.sender_username === myUsername ? 'me' : 'friend'}`}>
                            <div className="chat-bubble">{msg.message}</div>
                            {/* <div className="chat-ts">{msg.timestamp}</div> */}
                        </div>
                    ))}
                </div>
                
            {/* ── Input ── */}
                <div className="chat-input-row">
                    <input
                        className={`chat-input ${draft.length === 500 ? 'chat-input--error' : ''}`}
                        placeholder="Message…"
                        value={draft}
                        maxLength={500}
                        onChange={e => setDraft(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && send()}
                    />
                    <button
                        className="chat-send-btn"
                        onClick={send}
                        disabled={draft.length === 500}
                    >
                        {draft.length === 500 ? 'max 500 chars' : 'Send'}
                    </button>
                </div>
            </div>

        </div>
    )
}

export default ChatContainer
