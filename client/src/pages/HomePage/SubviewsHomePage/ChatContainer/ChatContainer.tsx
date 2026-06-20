import { useState } from 'react'
import { useChatContainer } from './useChatContainer'
import { OnlineIndicator } from '../../../../components/OnlineIndicator/OnlineIndicator'
import { cx } from '../../../../utils/cx'
import styles from './ChatContainer.module.css'

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
        chatContent = <div className={styles['chat-empty']}>Add Friends to message</div>
    } else {
        chatContent = thread.messages.filter(msg => msg.message).map((msg, i) => (
            <div key={i} className={cx(styles['chat-bubble-row'], msg.sender_username === thread.myUsername ? styles.me : styles.friend)}>
                <div className={styles['chat-bubble']}>{msg.message}</div>
            </div>
        ))
    }

    return (
        <div className={styles['chat-container']}>

            {/* ── Sidebar ── */}
            <div className={styles['chat-sidebar']}>
                <div className={styles['chat-sidebar-title']}>Messages</div>
                <div className={styles['chat-conv-list']}>
                    {sidebar.friendsList.map((f) => (
                        <div key={f.friend.id} className={cx(styles['friend-item'], f.friend.id === sidebar.activeId && styles.active)} onClick={() => sidebar.handleChooseTab(f.friend.id)}>
                            <div className={styles['friend-avatar']}>
                                {(f.friend.username ?? '?')[0].toUpperCase()}
                            </div>
                            <OnlineIndicator userId={f.friend.id} />
                            <span className={styles['friend-name']}>{f.friend.username}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* ── Thread ── */}
            <div className={styles['chat-thread']}>
                <div className={styles['chat-messages']} ref={thread.messagesRef} onScroll={thread.handleScroll}>
                    {thread.hasMore && thread.loadingOlder && <div className={styles['chat-load-older']}>Loading…</div>}
                    {chatContent}
                </div>

            {/* ── Input ── */}
                <div className={styles['chat-input-row']}>
                    <input
                        className={cx(styles['chat-input'], draft.length === 500 && styles['chat-input--error'])}
                        placeholder="Message…"
                        value={draft}
                        maxLength={500}
                        disabled={sidebar.noFriends}
                        onChange={e => setDraft(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && send()}
                    />
                    <button
                        className={styles['chat-send-btn']}
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
