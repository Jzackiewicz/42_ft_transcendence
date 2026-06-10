import { useState } from 'react'
import { useFriendsContext } from '../../../../context/FriendsListContext'

export function useChatContainer() {
    const { friendsList } = useFriendsContext()
    const [activeId, setActiveId] = useState<number>(0)

    const activeConversation = friendsList.find(f => f.friend.id === activeId) ?? friendsList[0]

    const handleSend = () => {
        // TODO: send via WebSocket
    }

    const handleChooseTab = (id: number) => {
        setActiveId(id)
    }

    return { friendsList, activeConversation, activeId, handleChooseTab, handleSend }
}
