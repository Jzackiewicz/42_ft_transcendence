import { useEffect, useState, useRef } from 'react'
import { useFriendsContext } from '../../../../context/FriendsListContext'
import { useUser } from '../../../../context/UserContext'
import { ChatMessage } from '../../../../types/Message'
import { getChatHistory, createChatSocket } from '../../../../api/socialsWrapper'

const PAGE_SIZE = 50
const BACKOFF_MS = [1000, 2000, 4000, 8000, 16000, 30000]

export type SocketStatus = 'connecting' | 'open' | 'closed'

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
    const { user, setUser } = useUser()
    const [activeId, setActiveId] = useState<number>(0)
    const [messages, setMessages] = useState<ChatMessage[]>([])
    const [offset, setOffset] = useState<number>(0)
    const [hasMore, setHasMore] = useState<boolean>(true)
    const [loadingOlder, setLoadingOlder] = useState<boolean>(false)
    const [historyError, setHistoryError] = useState<string | null>(null)
    const [socketStatus, setSocketStatus] = useState<SocketStatus>('closed')

    const socketRef = useRef<WebSocket | null>(null)
    const messagesRef = useRef<HTMLDivElement | null>(null)
    const shouldScrollRef = useRef<boolean>(true)

    useEffect(() => {
        if (activeId === 0 && friendsList.length > 0)
            setActiveId(friendsList[0].friend.id)
    }, [friendsList])

    useEffect(() => {
        if (!user || !activeId) {
            setSocketStatus('closed')
            return
        }

        let isCurrent = true
        let cancelled = false
        let reconnectTimer: ReturnType<typeof setTimeout> | null = null
        let reconnectAttempt = 0

        const roomName = getRoomName(user.id, activeId)

        setMessages([])
        setOffset(0)
        setHasMore(true)
        setHistoryError(null)
        setSocketStatus('connecting')
        shouldScrollRef.current = true

        const openSocket = () => {
            if (cancelled) return

            const ws = createChatSocket(roomName)
            socketRef.current = ws

            ws.onopen = () => {
                if (cancelled) return
                reconnectAttempt = 0
                setSocketStatus('open')
            }

            ws.onmessage = (event) => {
                let msg: ChatMessage
                try {
                    msg = JSON.parse(event.data)
                } catch {
                    return                     // ignore malformed payloads
                }
                if (msg.message) {
                    shouldScrollRef.current = true
                    setMessages(prev => [...prev, msg])
                }
            }

            ws.onerror = () => {
                // onerror fires just before onclose on a drop
                // nothing to do here: onclose decides whether to reconnect.
            }

            ws.onclose = (event) => {
                if (cancelled) return // intentional close (cleanup)
                if (event.code === 4001) {
                    setUser(null)
                    return
                }

                setSocketStatus('connecting')
                const idx = Math.min(reconnectAttempt, BACKOFF_MS.length - 1)
                const delay = BACKOFF_MS[idx]
                reconnectAttempt += 1
                reconnectTimer = setTimeout(() => {
                    reconnectTimer = null
                    openSocket()
                }, delay)
            }
        }

        openSocket()

        getChatHistory(roomName, 0)
            .then(data => {
                if (!isCurrent) return
                setMessages(data)
                setOffset(data.length)
                setHasMore(data.length === PAGE_SIZE)
            })
            .catch(() => {
                if (!isCurrent) return
                setHistoryError("Couldn't load messages. Please try again.")
            })

        return () => {
            isCurrent = false
            cancelled = true
            if (reconnectTimer) clearTimeout(reconnectTimer)
            socketRef.current?.close()
            socketRef.current = null
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
        getChatHistory(roomName, offset)
            .then(data => {
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
                setHistoryError(null) // clear if a retry-via-scroll succeeded
            })
            .catch(() => {
                setHistoryError("Couldn't load older messages.")
            })
            .finally(() => setLoadingOlder(false))
    }

    const handleScroll = () => {
        if (messagesRef.current && messagesRef.current.scrollTop === 0) {
            loadOlderMessages()
        }
    }

    const handleSend = (text: string): boolean => {
        if (!socketRef.current || !text.trim()) return false
        if (socketRef.current.readyState !== WebSocket.OPEN) return false
        socketRef.current.send(JSON.stringify({ message: text }))
        return true
    }

    const handleChooseTab = (id: number) => {
        setActiveId(id)
    }

    const noFriends = hasNoFriends(friendsList)

    return {
        sidebar: { friendsList, activeId, noFriends, handleChooseTab },
        thread:  { messages, myUsername: user?.username ?? '', messagesRef, loadingOlder, hasMore, handleScroll, historyError },
        input:   { handleSend, socketStatus }
    }
}
