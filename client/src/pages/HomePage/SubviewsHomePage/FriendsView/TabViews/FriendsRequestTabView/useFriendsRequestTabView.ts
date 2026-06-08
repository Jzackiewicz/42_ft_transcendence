import { useEffect, useState } from 'react'
import { getIncomingRequestsList, getOutgoingRequestsList } from '../../../../../../api/socialsWrapper'

interface PublicUser {
    id: number
    username: string
    avatar: string | null
}

export interface FriendRequest {
    id: number
    from_user: PublicUser
    to_user: PublicUser
}

export function useFriendsRequestTabView() {
    const [incomingRequestsList, setIncomingRequestsList] = useState<FriendRequest[]>([])
    const [outgoingRequestsList, setOutgoingRequestList] = useState<FriendRequest[]>([])

    useEffect(() => {
        getIncomingRequestsList().then(data => setIncomingRequestsList(data))
        getOutgoingRequestsList().then(data => setOutgoingRequestList(data))
    }, [])

    const handleAccept  = (id: number) => { console.log('accept',  id) }
    const handleDecline = (id: number) => { console.log('decline', id) }
    const handleCancel = (id: number) => { console.log('accept',  id) }

    return { incomingRequestsList, setIncomingRequestsList,
        outgoingRequestsList, setOutgoingRequestList,
        handleAccept, handleDecline, handleCancel
    }
}
