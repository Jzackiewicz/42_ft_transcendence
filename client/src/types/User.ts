export interface User {
    id: number
    username: string
    email: string
}

export interface PublicUser {
    id: number
    username: string
    avatar: string | null
}

export interface Friendship {
    friend: PublicUser
    created_at: string
}