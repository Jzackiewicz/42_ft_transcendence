import { useEffect, useState } from 'react'
import { getFriends } from '../../../../api/socialsWrapper'
import { Friendship } from '../../../../types/User'

export function useChatContainer() {
    const [friendsList, setFriendsList] = useState<Friendship[]>([])
    const [activeId, setActiveId] = useState<number>(0)

    useEffect(() => {
        getFriends().then(data => setFriendsList(Array.isArray(data) ? data : (data.results ?? [])))
    }, [])

    const activeConversation = friendsList.find(f => f.friend.id === activeId) ?? friendsList[0]

    const handleSend = () => {
        // TODO: send via WebSocket
    }

    const handleChooseTab = (id: number) => {
        setActiveId(id)
    }

    return { friendsList, activeConversation, activeId, handleChooseTab, handleSend }
}
