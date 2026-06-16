import { createContext, useContext, useState, useEffect, useCallback } from "react"
import { getFriends, getIncomingRequestsList, getOutgoingRequestsList } from "../api/socialsWrapper"
import { Friendship, FriendRequest } from "../types/User"

interface FriendsContextType {
    friendsList: Friendship[]
    incomingRequests: FriendRequest[]
    outgoingRequests: FriendRequest[]
    loading: boolean
    refresh: () => void
}

const FriendsContext = createContext<FriendsContextType | null>(null)

export function FriendsProvider({ children }: { children: React.ReactNode }) {
    const [friendsList, setFriendsList]         = useState<Friendship[]>([])
    const [incomingRequests, setIncomingRequests] = useState<FriendRequest[]>([])
    const [outgoingRequests, setOutgoingRequests] = useState<FriendRequest[]>([])
    const [loading, setLoading]                 = useState(false)

    const refresh = useCallback(() => {
        setLoading(true)
        // sync all network resoponses
        Promise.all([getFriends(), getIncomingRequestsList(), getOutgoingRequestsList()])
            .then(([friends, incoming, outgoing]) => {
                setFriendsList(Array.isArray(friends) ? friends : (friends.results ?? []))
                setIncomingRequests(incoming)
                setOutgoingRequests(outgoing)
            })
            .finally(() => setLoading(false))
    }, [])

    // is Used only once at mounting
    useEffect(() => {
        refresh()
    }, [])

    return (
        <FriendsContext.Provider value={{ friendsList, incomingRequests, outgoingRequests, loading, refresh }}>
            {children}
        </FriendsContext.Provider>
    )
}

export function useFriendsContext() {
    const context = useContext(FriendsContext)
    if (!context) throw new Error("useFriendsContext must be used inside FriendsProvider")
    return context
}
