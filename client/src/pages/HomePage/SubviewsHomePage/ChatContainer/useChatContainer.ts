import { useEffect, useState, useRef } from 'react'
import { useFriendsContext } from '../../../../context/FriendsListContext'
import { useUser } from '../../../../context/UserContext'
import { ChatMessage } from '../../../../types/Message'
import { getChatHistory, createChatSocket } from '../../../../api/socialsWrapper'

const PAGE_SIZE = 50

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
    const [offset, setOffset] = useState<number>(0)
    const [hasMore, setHasMore] = useState<boolean>(true)
    const [loadingOlder, setLoadingOlder] = useState<boolean>(false)

    const socketRef = useRef<WebSocket | null>(null)
    const messagesRef = useRef<HTMLDivElement | null>(null)
    const shouldScrollRef = useRef<boolean>(true)

    useEffect(() => {
        if (activeId === 0 && friendsList.length > 0)
            setActiveId(friendsList[0].friend.id)
    }, [friendsList])

    useEffect(() => {
        if (!user || !activeId)
            return

        let isCurrent = true
        setMessages([])
        setOffset(0)
        setHasMore(true)
        shouldScrollRef.current = true

        const roomName = getRoomName(user.id, activeId)
        socketRef.current?.close()
        socketRef.current = createChatSocket(roomName)
        socketRef.current.onmessage = (event) => {
            const msg: ChatMessage = JSON.parse(event.data)
            if (msg.message) {
                shouldScrollRef.current = true
                setMessages(prev => [...prev, msg])
            }
        }

        getChatHistory(roomName, 0).then(data => {
            if (isCurrent) {
                setMessages(data)
                setOffset(data.length)
                setHasMore(data.length === PAGE_SIZE)
            }
        })

        return () => {
            isCurrent = false
            socketRef.current?.close()
        }
    }, [activeId, user])

    // auto-scroll to bottom when new messages arrive
    useEffect(() => {
        if (shouldScrollRef.current && messagesRef.current && messages.length > 0) {
            messagesRef.current.scrollTop = messagesRef.current.scrollHeight
            shouldScrollRef.current = false
        }
    }, [messages])

    const loadOlderMessages = () => {
        if (!user || !activeId || loadingOlder || !hasMore)
            return

        const roomName = getRoomName(user.id, activeId)
        const container = messagesRef.current
        const scrollHeightBefore = container?.scrollHeight ?? 0

        setLoadingOlder(true)
        getChatHistory(roomName, offset).then(data => {
            if (data.length === 0) {
                setHasMore(false)
            } else {
                setMessages(prev => [...data, ...prev])
                setOffset(prev => prev + data.length)
                setHasMore(data.length === PAGE_SIZE)

                // restore scroll position so user doesn't jump to top
                requestAnimationFrame(() => {
                    if (container) {
                        container.scrollTop = container.scrollHeight - scrollHeightBefore
                    }
                })
            }
        }).finally(() => setLoadingOlder(false))
    }

    const handleScroll = () => {
        if (messagesRef.current && messagesRef.current.scrollTop === 0) {
            loadOlderMessages()
        }
    }

    const handleSend = (text: string) => {
        if (!socketRef.current || !text.trim()) return
        if (socketRef.current.readyState !== WebSocket.OPEN) return
        socketRef.current.send(JSON.stringify({ message: text }))
    }

    const handleChooseTab = (id: number) => {
        setActiveId(id)
    }

    const noFriends = hasNoFriends(friendsList)

    return {
        sidebar: { friendsList, activeId, noFriends, handleChooseTab },
        thread:  { messages, myUsername: user?.username ?? '', messagesRef, loadingOlder, hasMore, handleScroll },
        input:   { handleSend }
    }
}
