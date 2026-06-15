import { useEffect, useState } from 'react'
import { getIncomingRequestsList, getOutgoingRequestsList, 
    acceptFriendRequest, declineFriendRequest, cancelMyFriendRequest} from '../../../../../../api/socialsWrapper'

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
    const [refresh, setRefresh] = useState(0)

    useEffect(() => {
        getIncomingRequestsList().then(data => setIncomingRequestsList(data))
        getOutgoingRequestsList().then(data => setOutgoingRequestList(data))
    }, [refresh])

    const handleAccept  = async (requestID: number) => { await acceptFriendRequest(requestID);  setRefresh(prev => prev + 1) }
    const handleDecline = async (requestID: number) => { await declineFriendRequest(requestID); setRefresh(prev => prev + 1) }
    const handleCancel  = async (requestID: number) => { await cancelMyFriendRequest(requestID); setRefresh(prev => prev + 1) }

    return { incomingRequestsList, setIncomingRequestsList,
        outgoingRequestsList, setOutgoingRequestList,
        handleAccept, handleDecline, handleCancel
    }

}
