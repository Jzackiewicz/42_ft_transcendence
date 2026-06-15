import { useEffect, useRef, useState } from 'react'
import { searchFriends, sendFriendRequest } from '../../../../../../api/socialsWrapper'

interface RequestStatus {
    type: 'success' | 'error'
    message: string
}

export function useFriendsFindTabView() {
    const [searchQuery, setSearchQuery] = useState('')
    const [friends, setFriends] = useState<any[]>([])
    const [status, setStatus] = useState<RequestStatus | null>(null)
    const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

    useEffect(() => {
        if (searchQuery.length >= 2) {
            searchFriends(searchQuery).then(setFriends)
        } else {
            setFriends([])
        }
    }, [searchQuery])

    useEffect(() => () => { if (timerRef.current) clearTimeout(timerRef.current) }, [])

    function showStatus(s: RequestStatus) {
        if (timerRef.current) clearTimeout(timerRef.current)
        setStatus(s)
        timerRef.current = setTimeout(() => setStatus(null), 3000)
    }

    const handleSendRequest = async (username: string) => {
        const user = friends.find(f => f.username === username)
        if (!user) {
            showStatus({ type: 'error', message: 'Select a user from the list first' })
            return
        }
        try {
            await sendFriendRequest(user.id)
            showStatus({ type: 'success', message: `Request sent to ${user.username}!` })
        } catch (error: any) {
            const msg = error?.response?.data?.error?.[0]
                ?? error?.response?.data?.detail
                ?? 'Failed to send request'
            showStatus({ type: 'error', message: msg })
        }
    }

    return { searchQuery, setSearchQuery, handleSendRequest, friends, status }
}
