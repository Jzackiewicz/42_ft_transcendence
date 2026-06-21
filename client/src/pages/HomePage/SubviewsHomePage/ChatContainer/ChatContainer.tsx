import { ChatInner } from '../../../../components/chat/ChatInner'
import styles from '../../../../components/chat/chat.module.css'

function ChatContainer() {
    return (
        <div className={styles.chatContainer}>
            <ChatInner />
        </div>
    )
}

export default ChatContainer
