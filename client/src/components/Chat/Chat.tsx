import { useState } from 'react'
import { useChat } from './useChat'
import { ErrorBanner } from '../ErrorBanner/ErrorBanner'
import { Button } from '../Button/Button'
import { cx } from '../../utils/cx'
import styles from './Chat.module.css'
import { Avatar } from '../Avatar/Avatar'
import { Icon } from '../Icon/Icon'

const MAX_MESSAGE_LENGTH = 500

/*
 * Shared inner content of the chat: sidebar (friend list) + thread
 * (messages, error banner, connection hint) + input row.
 */
export function Chat() {
    const { sidebar, thread, input } = useChat()
    const [draft, setDraft] = useState('')
    const [showThreadMobile, setShowThreadMobile] = useState(false)

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
        chatContent = <div className={styles.chatEmpty}>Add Friends to message</div>
    } else {
        chatContent = thread.messages.filter(msg => msg.message).map((msg, i) => (
            <div
                key={i}
                className={cx(styles.chatBubbleRow, msg.sender_username === thread.myUsername ? styles.me : styles.friend)}
            >
                <div className={styles.chatBubble}>{msg.message}</div>
            </div>
        ))
    }

    return (
        <>
            {/* ── Sidebar ── */}
            <div className={cx(styles.chatSidebar, showThreadMobile && styles.mobileHidden)}>
                <div className={styles.chatSidebarTitle}>Messages</div>
                <div className={styles.chatConvList}>
                    {sidebar.friendsList.map(f => (
                        <div
                            key={f.friend.id}
                            className={cx(styles.friendItem, f.friend.id === sidebar.activeId && styles.active)}
                            onClick={() => {
                                sidebar.handleChooseTab(f.friend.id)
                                setShowThreadMobile(true)
                            }}
                        >
                            <Avatar name={f.friend.username} imageUrl={f.friend.avatar} size="md" userId={f.friend.id} />
                            <span className={styles.friendName}>{f.friend.username}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* ── Thread ── */}
            <div className={cx(styles.chatThread, !showThreadMobile && styles.mobileHidden)}>
                <div className={styles.chatMobileHeader}>
                    <button
                        className={styles.chatMobileBackBtn}
                        onClick={() => setShowThreadMobile(false)}
                    >
                        <Icon name="arrowLeft" size="sm" /> Back to list
                    </button>
                </div>

                <div
                    className={styles.chatMessages}
                    ref={thread.messagesRef}
                    onScroll={thread.handleScroll}
                >
                    {thread.historyError && (
                        <ErrorBanner
                            message={thread.historyError}
                            action={
                                <Button variant="dangerGhost" size="sm" onClick={thread.retryHistory}>
                                    Retry
                                </Button>
                            }
                        />
                    )}
                    {thread.hasMore && thread.loadingOlder && (
                        <div className={styles.chatLoadOlder}>Loading…</div>
                    )}
                    {chatContent}
                </div>

                {notConnected && !sidebar.noFriends && (
                    <div className={styles.chatConnHint} role="status">Reconnecting…</div>
                )}

                {/* ── Input ── */}
                <div className={styles.chatInputRow}>
                    <input
                        className={cx(styles.chatInput, draft.length === MAX_MESSAGE_LENGTH && styles.chatInputError)}
                        placeholder={notConnected ? 'Reconnecting…' : 'Message…'}
                        value={draft}
                        maxLength={MAX_MESSAGE_LENGTH}
                        disabled={isDisabled}
                        onChange={e => setDraft(e.target.value)}
                        onKeyDown={e => e.key === 'Enter' && send()}
                    />
                    <button
                        className={styles.chatSendBtn}
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

export default Chat
