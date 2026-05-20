import { createContext, useContext, useState, useEffect } from "react"
import {getMe} from "../api/apiWrapper"

interface User {
    id: number
    username: string
    email: string
}

interface UserContextType {
    user: User | null | undefined //user 
    setUser: (user: User | null) => void
}

const UserContext = createContext<UserContextType | null>(null)

export function UserProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null | undefined>(undefined)

    useEffect(() => {
        getMe().then(data => {
            setUser(data ?? null)
        })
    }, [])

    return (
        <UserContext.Provider value={{ user, setUser }}>
            {children}
        </UserContext.Provider>
    )
}

export function useUser() {
    const context = useContext(UserContext)
    if (!context) throw new Error("useUser must be used inside UserProvider")
    return context
}
