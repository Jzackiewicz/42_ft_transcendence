import { useState } from 'react'
import { useChatContainer } from './useChatContainer'
import { OnlineIndicator } from '../OnlineIndicator/OnlineIndicator'
import { cx } from '../../utils/cx'
import styles from './chat.module.css'

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
        chatContent = <div className={styles['chat-empty']}>Add Friends to message</div>
    } else {
        chatContent = thread.messages.filter(msg => msg.message).map((msg, i) => (
            <div
                key={i}
                className={cx(styles['chat-bubble-row'], msg.sender_username === thread.myUsername ? styles.me : styles.friend)}
            >
                <div className={styles['chat-bubble']}>{msg.message}</div>
            </div>
        ))
    }

    return (
        <>
            {/* ── Sidebar ── */}
            <div className={styles['chat-sidebar']}>
                <div className={styles['chat-sidebar-title']}>Messages</div>
                <div className={styles['chat-conv-list']}>
                    {sidebar.friendsList.map(f => (
                        <div
                            key={f.friend.id}
                            className={cx(styles['friend-item'], f.friend.id === sidebar.activeId && styles.active)}
                            onClick={() => sidebar.handleChooseTab(f.friend.id)}
                        >
                            <div className={styles['friend-avatar']}>
                                {(f.friend.username ?? '?')[0].toUpperCase()}
                                <OnlineIndicator userId={f.friend.id} />
                            </div>
                            <span className={styles['friend-name']}>{f.friend.username}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* ── Thread ── */}
            <div className={styles['chat-thread']}>
                <div
                    className={styles['chat-messages']}
                    ref={thread.messagesRef}
                    onScroll={thread.handleScroll}
                >
                    {thread.historyError && (
                        <div className={styles['chat-error']} role="alert">
                            <span>{thread.historyError}</span>
                            <button className={styles['chat-error-retry']} onClick={thread.retryHistory}>
                                Retry
                            </button>
                        </div>
                    )}
                    {thread.hasMore && thread.loadingOlder && (
                        <div className={styles['chat-load-older']}>Loading…</div>
                    )}
                    {chatContent}
                </div>

                {notConnected && !sidebar.noFriends && (
                    <div className={styles['chat-conn-hint']} role="status">Reconnecting…</div>
                )}

                {/* ── Input ── */}
                <div className={styles['chat-input-row']}>
                    <input
                        className={cx(styles['chat-input'], draft.length === MAX_MESSAGE_LENGTH && styles['chat-input--error'])}
                        placeholder={notConnected ? 'Reconnecting…' : 'Message…'}
                        value={draft}
                        maxLength={MAX_MESSAGE_LENGTH}
                        disabled={isDisabled}
                        onChange={e => setDraft(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && send()}
                    />
                    <button
                        className={styles['chat-send-btn']}
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
