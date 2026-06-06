import { useState } from 'react'

export interface FriendRequest {
    id: number
    username: string
}

export function useFriendsRequestTabView() {
    const [requests] = useState<FriendRequest[]>([
        { id: 1, username: 'Luna'   },
        { id: 2, username: 'Cosmos' },
                { id: 1, username: 'Luna'   },
        { id: 2, username: 'Cosmos' },
                { id: 1, username: 'Luna'   },
        { id: 2, username: 'Cosmos' },
                { id: 1, username: 'Luna'   },
        { id: 2, username: 'Cosmos' },
    ])

    const handleAccept  = (id: number) => { console.log('accept',  id) }
    const handleDecline = (id: number) => { console.log('decline', id) }

    return { requests, handleAccept, handleDecline }
}
