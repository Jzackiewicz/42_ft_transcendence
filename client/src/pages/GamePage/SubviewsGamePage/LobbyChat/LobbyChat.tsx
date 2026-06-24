import { Chat } from '../../../../components/Chat/Chat'
import { cx } from '../../../../utils/cx'
import shared from '../../../../components/Chat/Chat.module.css'
import styles from './LobbyChat.module.css'

export function LobbyChat() {
    return (
        <div className={cx(shared.chatContainer, styles.lobbyChat)}>
            <Chat />
        </div>
    )
}
