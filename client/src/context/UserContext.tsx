import { createContext, useContext, useState } from "react"

interface User {
    id: number
    username: string
    email: string
}

interface UserContextType {
    user: User | null
    setUser: (user: User | null) => void
}

const UserContext = createContext<UserContextType | null>(null)


//Singletone - the real userData holder
export function UserProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
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
