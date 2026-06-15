import { acceptFriendRequest, declineFriendRequest, cancelMyFriendRequest } from '../../../../../../api/socialsWrapper'
import { useFriendsContext } from '../../../../../../context/FriendsListContext'
import { FriendRequest } from '../../../../../../types/User'

export type { FriendRequest }

export function useFriendsRequestTabView() {
    const { incomingRequests, outgoingRequests, loading, refresh } = useFriendsContext()

    const handleAccept  = async (requestID: number) => { await acceptFriendRequest(requestID);  refresh() }
    const handleDecline = async (requestID: number) => { await declineFriendRequest(requestID); refresh() }
    const handleCancel  = async (requestID: number) => { await cancelMyFriendRequest(requestID); refresh() }

    return {
        incomingRequestsList: incomingRequests,
        outgoingRequestsList: outgoingRequests,
        loading,
        handleAccept, handleDecline, handleCancel,
    }
}
