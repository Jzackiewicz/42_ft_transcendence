import { useEffect, useState, useRef } from 'react'
import { useFriendsContext } from '../../../../context/FriendsListContext'
import { useUser } from '../../../../context/UserContext'
import { ChatMessage } from '../../../../types/Message'
import { getChatHistory, createChatSocket } from '../../../../api/socialsWrapper'

function getRoomName(myId: number, friendId: number): string {
    return `dm_${Math.min(myId, friendId)}_${Math.max(myId, friendId)}`
}

export function useChatContainer() {
    const { friendsList } = useFriendsContext()
    const { user } = useUser()
    const [activeId, setActiveId] = useState<number>(0)
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const socketRef = useRef<WebSocket | null>(null)

    const selectedFriend = friendsList.find(f => f.friend.id === activeId) ?? friendsList[0]

    useEffect(() => {
        if (!user || !activeId)
            return

        const roomName = getRoomName(user.id, activeId)
        socketRef.current?.close()
        socketRef.current = createChatSocket(roomName)
        socketRef.current.onmessage = (event) => {
            const msg: ChatMessage = JSON.parse(event.data)
            setMessages(prev => [...prev, msg])
        }

        getChatHistory(roomName).then(data => setMessages(data))
        return () => { socketRef.current?.close() }
    }, [activeId, user])

    const handleSend = (text: string) => {
        if (!socketRef.current || !text.trim()) return
        if (socketRef.current.readyState !== WebSocket.OPEN) return
        socketRef.current.send(JSON.stringify({ message: text }))
    }

    const handleChooseTab = (id: number) => {
        setActiveId(id)
    }

    return { friendsList, selectedFriend, activeId, messages, myUsername: user?.username ?? '', handleChooseTab, handleSend }
}
