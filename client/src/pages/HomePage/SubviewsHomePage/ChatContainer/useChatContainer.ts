import { useEffect, useState, useRef } from 'react'
import { useFriendsContext } from '../../../../context/FriendsListContext'
import { useUser } from '../../../../context/UserContext'
import { ChatMessage } from '../../../../types/Message'
import { getChatHistory, createChatSocket } from '../../../../api/socialsWrapper'

function hasNoFriends(friendsList: { friend: { id: number } }[]): boolean {
    var friendsAreEmpty: boolean
    if (friendsList.length == 0) {
        friendsAreEmpty = true
    } else {
        friendsAreEmpty = false
    }
    return friendsAreEmpty
}

function getRoomName(myId: number, friendId: number): string {
    return `dm_${Math.min(myId, friendId)}_${Math.max(myId, friendId)}`
}

export function useChatContainer() {
    const { friendsList } = useFriendsContext()
    const { user } = useUser()
    const [activeId, setActiveId] = useState<number>(0)
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const socketRef = useRef<WebSocket | null>(null)

    useEffect(() => {
        if (activeId === 0 && friendsList.length > 0)
            setActiveId(friendsList[0].friend.id)
    }, [friendsList])

    useEffect(() => {
        if (!user || !activeId)
            return

        let isCurrent = true

        const roomName = getRoomName(user.id, activeId)
        socketRef.current?.close()
        socketRef.current = createChatSocket(roomName)
        socketRef.current.onmessage = (event) => {
            const msg: ChatMessage = JSON.parse(event.data)
            if (msg.message) setMessages(prev => [...prev, msg])
        }

        getChatHistory(roomName).then(data => {
            if (isCurrent) setMessages(data)
        })

        return () => {
            isCurrent = false
            socketRef.current?.close()
        }
    }, [activeId, user])

    const handleSend = (text: string) => {
        if (!socketRef.current || !text.trim()) return
        if (socketRef.current.readyState !== WebSocket.OPEN) return
        socketRef.current.send(JSON.stringify({ message: text }))
    }

    const handleChooseTab = (id: number) => {
        setActiveId(id)
    }

    const noFriends = hasNoFriends(friendsList)

    return { friendsList, activeId, messages, myUsername: user?.username ?? '', noFriends, handleChooseTab, handleSend }
}
