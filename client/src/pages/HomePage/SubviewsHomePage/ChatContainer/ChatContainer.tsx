import { ChatInner } from '../../../../components/chat/ChatInner'

/**
 * HomePage chat shell. All UI lives in <ChatInner /> — this file just
 * provides the outer layout (220px sidebar, fixed height) via the
 * .chat-container class, which is styled in components/chat/chat.css
 * (loaded transitively by ChatInner).
 */
function ChatContainer() {
    return (
        <div className="chat-container">
            <ChatInner />
        </div>
    )
}

export default ChatContainer
