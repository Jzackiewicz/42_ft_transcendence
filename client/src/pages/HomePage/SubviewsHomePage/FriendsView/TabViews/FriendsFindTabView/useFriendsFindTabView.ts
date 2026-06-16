import { useEffect, useRef, useState } from 'react'
import { searchFriends, sendFriendRequest } from '../../../../../../api/socialsWrapper'
import { useFriendsContext } from '../../../../../../context/FriendsListContext'

interface RequestStatus {
    type: 'success' | 'error'
    message: string
}

export function useFriendsFindTabView() {
    const { refresh } = useFriendsContext()
    const [searchQuery, setSearchQuery] = useState('')
    const [friends, setFriends] = useState<any[]>([])
    const [status, setStatus] = useState<RequestStatus | null>(null)
    const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

    useEffect(() => {
        if (searchQuery.length >= 2) {
            searchFriends(searchQuery).then(results => setFriends(results))
        } else {
            setFriends([])
        }
    }, [searchQuery])

    function showStatus(type: 'success' | 'error', message: string) {
        clearTimeout(timerRef.current ?? undefined)
        setStatus({ type, message })
        timerRef.current = setTimeout(() => setStatus(null), 3000)
    }

    const handleSendRequest = async (username: string) => {
        const user = friends.find(f => f.username === username)
        if (!user) {
            showStatus('error', 'Select a user from the list first')
            return
        }
        try {
            await sendFriendRequest(user.id)
            refresh()
            showStatus('success', `Request sent to ${user.username}!`)
        } catch (error: any) {
            const msg = error?.response?.data?.error?.[0]
                ?? error?.response?.data?.detail
                ?? 'Failed to send request'
            showStatus('error', msg)
        }
    }

    return { searchQuery, setSearchQuery, handleSendRequest, friends, status }
}
