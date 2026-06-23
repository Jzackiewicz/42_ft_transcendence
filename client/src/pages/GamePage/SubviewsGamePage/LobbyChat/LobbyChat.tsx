import { ChatInner } from '../../../../components/chat/ChatInner'
import { cx } from '../../../../utils/cx'
import shared from '../../../../components/chat/chat.module.css'
import styles from './LobbyChat.module.css'

export function LobbyChat() {
    return (
        <div className={cx(shared.chatContainer, styles.lobbyChat)}>
            <ChatInner />
        </div>
    )
}
