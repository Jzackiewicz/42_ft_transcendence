import { useRef, useState } from 'react'
import { acceptFriendRequest, declineFriendRequest, cancelMyFriendRequest } from '../../../../../../api/socialsWrapper'
import { useFriendsContext } from '../../../../../../context/FriendsListContext'
import { FriendRequest } from '../../../../../../types/User'

export type { FriendRequest }

export function useFriendsRequestTabView() {
    const { incomingRequests, outgoingRequests, loading, refresh } = useFriendsContext()
    const [error, setError] = useState<string | null>(null)
    const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

    function showError() {
        clearTimeout(timerRef.current ?? undefined)
        setError('Error during update, try one more time')
        timerRef.current = setTimeout(() => setError(null), 3000)
    }

    const handleAccept  = async (requestID: number) => { try { await acceptFriendRequest(requestID);  refresh() } catch { showError() } }
    const handleDecline = async (requestID: number) => { try { await declineFriendRequest(requestID); refresh() } catch { showError() } }
    const handleCancel  = async (requestID: number) => { try { await cancelMyFriendRequest(requestID); refresh() } catch { showError() } }

    return {
        incomingRequestsList: incomingRequests,
        outgoingRequestsList: outgoingRequests,
        loading,
        error,
        handleAccept, handleDecline, handleCancel,
    }
}
