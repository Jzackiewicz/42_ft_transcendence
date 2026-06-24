import { Chat } from '../../../../components/Chat/Chat'
import styles from '../../../../components/Chat/Chat.module.css'

function ChatContainer() {
    return (
        <div className={styles.chatContainer}>
            <Chat />
        </div>
    )
}

export default ChatContainer
