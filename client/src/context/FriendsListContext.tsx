import { createContext, useContext, useState, useEffect, useCallback } from "react"
import { getFriends } from "../api/socialsWrapper"
import { Friendship } from "../types/User"

interface FriendsContextType {
    friendsList: Friendship[]
    refresh: () => void
}

const FriendsContext = createContext<FriendsContextType | null>(null)

export function FriendsProvider({ children }: { children: React.ReactNode }) {
    const [friendsList, setFriendsList] = useState<Friendship[]>([])

    const refresh = useCallback(() => {
        getFriends().then(data => setFriendsList(Array.isArray(data) ? data : (data.results ?? [])))
    }, [])

    useEffect(() => {
        refresh()
    }, [refresh])

    return (
        <FriendsContext.Provider value={{ friendsList, refresh }}>
            {children}
        </FriendsContext.Provider>
    )
}

export function useFriendsContext() {
    const context = useContext(FriendsContext)
    if (!context) throw new Error("useFriendsContext must be used inside FriendsProvider")
    return context
}
