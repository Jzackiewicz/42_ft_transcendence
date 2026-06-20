import { useState } from 'react'
import { useChatContainer } from './useChatContainer'
import { OnlineIndicator } from '../../../../components/OnlineIndicator/OnlineIndicator'
import './ChatContainer.css'

function ChatContainer() {
    const { sidebar, thread, input } = useChatContainer()
    const [draft, setDraft] = useState('')

    const send = () => {
        input.handleSend(draft)
        setDraft('')
    }

    let sendBtnLabel
    if (draft.length === 500) {
        sendBtnLabel = 'max 500 chars'
    } else {
        sendBtnLabel = 'Send'
    }

    let chatContent
    if (sidebar.noFriends) {
        chatContent = <div className="chat-empty">Add Friends to message</div>
    } else {
        chatContent = thread.messages.filter(msg => msg.message).map((msg, i) => (
            <div key={i} className={`chat-bubble-row ${msg.sender_username === thread.myUsername ? 'me' : 'friend'}`}>
                <div className="chat-bubble">{msg.message}</div>
            </div>
        ))
    }

    return (
        <div className="chat-container">

            {/* ── Sidebar ── */}
            <div className="chat-sidebar">
                <div className="chat-sidebar-title">Messages</div>
                <div className="chat-conv-list">
                    {sidebar.friendsList.map((f) => (
                        <div key={f.friend.id} className={`friend-item ${f.friend.id === sidebar.activeId ? 'active' : ''}`} onClick={() => sidebar.handleChooseTab(f.friend.id)}>
                            <div className="friend-avatar">
                                {(f.friend.username ?? '?')[0].toUpperCase()}
                                <OnlineIndicator userId={f.friend.id} />
                            </div>
                            <span className="friend-name">{f.friend.username}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* ── Thread ── */}
            <div className="chat-thread">
                <div className="chat-messages" ref={thread.messagesRef} onScroll={thread.handleScroll}>
                    {thread.hasMore && thread.loadingOlder && <div className="chat-load-older">Loading…</div>}
                    {chatContent}
                </div>

            {/* ── Input ── */}
                <div className="chat-input-row">
                    <input
                        className={`chat-input ${draft.length === 500 ? 'chat-input--error' : ''}`}
                        placeholder="Message…"
                        value={draft}
                        maxLength={500}
                        disabled={sidebar.noFriends}
                        onChange={e => setDraft(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && send()}
                    />
                    <button
                        className="chat-send-btn"
                        onClick={send}
                        disabled={sidebar.noFriends || draft.length === 500}
                    >
                        {sendBtnLabel}
                    </button>
                </div>
            </div>

        </div>
    )
}

export default ChatContainer
