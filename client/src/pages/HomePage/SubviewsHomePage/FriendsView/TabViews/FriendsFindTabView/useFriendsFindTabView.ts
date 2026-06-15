import { useEffect, useState } from 'react'
import { searchFriends, sendFriendRequest } from '../../../../../../api/socialsWrapper'

async function updateSearchRes(query: string, setFriends: (data: any[]) => void) {
    if (query.length >= 2) {
        const friends = await searchFriends(query)
        setFriends(friends)
    }
}

export function useFriendsFindTabView() {
    const [searchQuery, setSearchQuery] = useState('')
    const [friends, setFriends] = useState<any[]>([])

    useEffect(() => {
        updateSearchRes(searchQuery, setFriends)
    }, [searchQuery])

    const handleSendRequest = (username: string) => {
        const user = friends.find(f => f.username === username)
        if (user) {
            sendFriendRequest(user.id)
        }
    }

    return { searchQuery, setSearchQuery, handleSendRequest, friends}
}
