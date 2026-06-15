import { createContext, useContext, useState, useEffect } from "react"
import { getMe } from "../api/authWrapper"
import { User } from "../types/User"


interface UserContextType {
    user: User | null | undefined //user 
    setUser: (user: User | null) => void
    activeSessionUuid: string | null
    setActiveSessionUuid: (uuid: string | null) => void
}

const UserContext = createContext<UserContextType | null>(null)

export function UserProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null | undefined>(undefined)
    const [activeSessionUuid, setActiveSessionUuidState] = useState<string | null>(localStorage.getItem('activeSessionUuid'))

    const setActiveSessionUuid = (uuid: string | null) => {
        if (uuid) {
            localStorage.setItem('activeSessionUuid', uuid)
        } else {
            localStorage.removeItem('activeSessionUuid')
        }
        setActiveSessionUuidState(uuid)
    }

    useEffect(() => {
        getMe().then(data => {
            setUser(data ?? null)
        })
    }, [])

    return (
        <UserContext.Provider value={{ user, setUser, activeSessionUuid, setActiveSessionUuid }}>
            {children}
        </UserContext.Provider>
    )
}

export function useUser() {
    const context = useContext(UserContext)
    if (!context) throw new Error("useUser must be used inside UserProvider")
    return context
}
