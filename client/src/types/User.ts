export interface User {
    id: number
    username: string
    email: string
}

export interface PublicUser {
    id: number
    username: string
    avatar: string | null
    is_online: boolean
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