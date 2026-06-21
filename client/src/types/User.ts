export interface User {
    id: number
    username: string
    email: string
    date_joined: string
    avatar: string | null
}

export interface PublicUser {
    id: number
    username: string
    avatar: string | null
    is_online: boolean
    date_joined: string
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