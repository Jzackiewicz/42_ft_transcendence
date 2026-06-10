import { useEffect, useState } from 'react'
import { useFriendsContext } from '../../../../context/FriendsListContext'
import { useUser } from '../../../../context/UserContext'
import { ChatMessage } from '../../../../types/Message'
import { getChatHistory } from '../../../../api/socialsWrapper'

function getRoomName(myId: number, friendId: number): string {
    return `dm_${Math.min(myId, friendId)}_${Math.max(myId, friendId)}`
}

export function useChatContainer() {
    const { friendsList } = useFriendsContext()
    const { user } = useUser()
    const [activeId, setActiveId] = useState<number>(0)
    const [messages, setMessages] = useState<ChatMessage[]>([])

    const activeConversation = friendsList.find(f => f.friend.id === activeId) ?? friendsList[0]

    useEffect(() => {
        if (!user || !activeId) 
            return
        const roomName = getRoomName(user.id, activeId)
        getChatHistory(roomName).then(data => setMessages(data))
    }, [activeId, user])

    const handleSend = () => {
        // TODO: send via WebSocket
    }

    const handleChooseTab = (id: number) => {
        setActiveId(id)
    }

    return { friendsList, activeId, messages, myUsername: user?.username ?? '', handleChooseTab, handleSend }
}
