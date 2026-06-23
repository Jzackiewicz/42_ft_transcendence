import { ChatInner } from '../../../../components/chat/ChatInner'
import styles from './LobbyChat.module.css'

export function LobbyChat() {
    return (
        <div className={styles.lobbyChat}>
            <ChatInner />
        </div>
    )
}
