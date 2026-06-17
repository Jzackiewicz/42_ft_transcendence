import { apiClient } from './apiClient';

export async function getFriends() {
    const res = await apiClient.get('social/friends/')
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

export async function acceptFriendRequest(requestId: number) {
    const res = await apiClient.patch(`/social/friend-requests/${requestId}/`, { action: 'accept' })
    return res.data
}

export async function declineFriendRequest(requestId: number) {
    const res = await apiClient.patch(`/social/friend-requests/${requestId}/`, { action: 'decline' })
    return res.data
}

export async function cancelMyFriendRequest(requestId: number) {
    await apiClient.delete(`/social/friend-requests/${requestId}/`)
}

export async function getOutgoingRequestsList() {
    const res = await apiClient.get('/social/friend-requests/outgoing/')
    return res.data
}

export async function deleteFromFriends(userId: number) {
    await apiClient.delete(`/social/friends/${userId}/`)
}


export async function getChatHistory(room_name: string, offset: number = 0) {
    const res = await apiClient.get(`/social/chat/${room_name}/history/`, { params: { offset } })
    return res.data
}

export function createChatSocket(roomName: string): WebSocket {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    return new WebSocket(`${protocol}//${host}/ws/chat/${roomName}/`)
}
