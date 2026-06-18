export interface User {
    id: number
    username: string
    email: string
    avatar: string | null
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

export interface FriendRequest {
    id: number
    from_user: PublicUser
    to_user: PublicUser
}