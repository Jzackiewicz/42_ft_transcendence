import { apiClient } from './apiClient';

export async function getFriends() {
    const res = await apiClient.get('socials/friends/')
    return res.data
}

//Backend requires text min 2 chars
export async function searchFriends(text: string) {
    const res = await apiClient.get('social/friends/search/', { params: { q: text } })
    return res.data
}

export async function sendFriendRequest(futureFriendID: number) {
    const res = await apiClient.post('social/friend-requests/', { to_user_id: futureFriendID })

    return res.data
}

export async function getIncomingRequestsList() {
    const res = await apiClient.get('/social/friend-requests/incoming/')
    return res.data
}

export async function getOutgoingRequestsList() {
    const res = await apiClient.get('/social/friend-requests/outgoing/')
    return res.data
}