import { useState } from 'react'

export function useFriendsFindTabView() {
    const [searchQuery, setSearchQuery] = useState('')

    const handleSendRequest = (username: string) => { console.log('request', username) }

    return { searchQuery, setSearchQuery, handleSendRequest }
}
