import { useState } from 'react'
import { useChatContainer } from './useChatContainer'
import { OnlineIndicator } from '../OnlineIndicator'
import './chat.css'

const MAX_MESSAGE_LENGTH = 500

/*
 * Shared inner content of the chat: sidebar (friend list) + thread
 * (messages, error banner, connection hint) + input row.
 */
export function ChatInner() {
    const { sidebar, thread, input } = useChatContainer()
    const [draft, setDraft] = useState('')

    const notConnected = input.socketStatus !== 'open'
    const isDisabled = sidebar.noFriends || notConnected

    const send = () => {
        if (!draft.trim()) return
        const ok = input.handleSend(draft)
        if (ok) setDraft('') // keep draft on failure so user can retry
    }

    const sendBtnLabel = draft.length === MAX_MESSAGE_LENGTH ? `max ${MAX_MESSAGE_LENGTH} chars` : 'Send'

    let chatContent
    if (sidebar.noFriends) {
        chatContent = <div className="chat-empty">Add Friends to message</div>
    } else {
        chatContent = thread.messages.filter(msg => msg.message).map((msg, i) => (
            <div
                key={i}
                className={`chat-bubble-row ${msg.sender_username === thread.myUsername ? 'me' : 'friend'}`}
            >
                <div className="chat-bubble">{msg.message}</div>
            </div>
        ))
    }

    return (
        <>
            {/* ── Sidebar ── */}
            <div className="chat-sidebar">
                <div className="chat-sidebar-title">Messages</div>
                <div className="chat-conv-list">
                    {sidebar.friendsList.map(f => (
                        <div
                            key={f.friend.id}
                            className={`friend-item ${f.friend.id === sidebar.activeId ? 'active' : ''}`}
                            onClick={() => sidebar.handleChooseTab(f.friend.id)}
                        >
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
                <div
                    className="chat-messages"
                    ref={thread.messagesRef}
                    onScroll={thread.handleScroll}
                >
                    {thread.historyError && (
                        <div className="chat-error" role="alert">
                            <span>{thread.historyError}</span>
                            <button className="chat-error-retry" onClick={thread.retryHistory}>
                                Retry
                            </button>
                        </div>
                    )}
                    {thread.hasMore && thread.loadingOlder && (
                        <div className="chat-load-older">Loading…</div>
                    )}
                    {chatContent}
                </div>

                {notConnected && !sidebar.noFriends && (
                    <div className="chat-conn-hint" role="status">Reconnecting…</div>
                )}

                {/* ── Input ── */}
                <div className="chat-input-row">
                    <input
                        className={`chat-input ${draft.length === MAX_MESSAGE_LENGTH ? 'chat-input--error' : ''}`}
                        placeholder={notConnected ? 'Reconnecting…' : 'Message…'}
                        value={draft}
                        maxLength={MAX_MESSAGE_LENGTH}
                        disabled={isDisabled}
                        onChange={e => setDraft(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && send()}
                    />
                    <button
                        className="chat-send-btn"
                        onClick={send}
                        disabled={isDisabled || draft.length === MAX_MESSAGE_LENGTH}
                    >
                        {sendBtnLabel}
                    </button>
                </div>
            </div>
        </>
    )
}

export default ChatInner
