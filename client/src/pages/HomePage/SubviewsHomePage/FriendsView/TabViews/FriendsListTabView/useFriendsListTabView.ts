import { useEffect, useState } from 'react'
import { getFriends, deleteFromFriends } from '../../../../../../api/socialsWrapper'

export interface PublicUser {
    id: number
    username: string
    avatar: string | null
}

export interface Friendship {
    friend: PublicUser
    created_at: string
}

export function useFriendsListTabView() {
    const [friendsList, setFriendsList] = useState<Friendship[]>([])
    const [refreshTab, setRefreshTab] = useState(0)

    useEffect(() => {
        getFriends().then(data => setFriendsList(Array.isArray(data) ? data : (data.results ?? [])))
    }, [refreshTab])

    const handleRemove = async (userId: number) => { await deleteFromFriends(userId); setRefreshTab(prev => prev + 1) }

    return { friendsList, handleRemove }
}
