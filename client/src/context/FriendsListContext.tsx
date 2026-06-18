import { createContext, useContext, useState, useEffect, useCallback } from "react"
import { getFriends, getIncomingRequestsList, getOutgoingRequestsList } from "../api/socialsWrapper"
import { Friendship, FriendRequest } from "../types/User"
import { usePresence } from "./PresenceContext"

interface FriendsContextType {
    friendsList: Friendship[]
    incomingRequests: FriendRequest[]
    outgoingRequests: FriendRequest[]
    loading: boolean
    refresh: () => void
}

const FriendsContext = createContext<FriendsContextType | null>(null)

export function FriendsProvider({ children }: { children: React.ReactNode }) {
    const { seed } = usePresence()
    const [friendsList, setFriendsList]         = useState<Friendship[]>([])
    const [incomingRequests, setIncomingRequests] = useState<FriendRequest[]>([])
    const [outgoingRequests, setOutgoingRequests] = useState<FriendRequest[]>([])
    const [loading, setLoading]                 = useState(false)

    const refresh = useCallback(() => {
        setLoading(true)
        // sync all network resoponses
        Promise.all([getFriends(), getIncomingRequestsList(), getOutgoingRequestsList()])
            .then(([friends, incoming, outgoing]) => {
                const list = Array.isArray(friends) ? friends : (friends.results ?? [])
                setFriendsList(list)
                setIncomingRequests(incoming)
                setOutgoingRequests(outgoing)
                seed(list.map((f: Friendship) => ({
                    id: f.friend.id,
                    is_online: f.friend.is_online,
                })))
            })
            .finally(() => setLoading(false))
    }, [seed])

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
