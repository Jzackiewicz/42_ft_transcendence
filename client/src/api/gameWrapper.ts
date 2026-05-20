import { apiClient } from './apiClient';

export async function createLobby() {
    const res = await apiClient.post('/game/lobby/create/');
    return res.data;
}

export async function joinLobby(joinUuid: string) {
    await apiClient.post(`/game/lobby/join/${joinUuid}/`);
}

// ws: — plain WebSocket (like http://)
// wss: — secure WebSocket (like https://)
export function connectGameSocket(sessionUuid: string): WebSocket {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return new WebSocket(`${wsProtocol}//${window.location.host}/ws/game/${sessionUuid}/`);
}

export function connectChatSocket(roomName: string): WebSocket {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return new WebSocket(`${wsProtocol}//${window.location.host}/ws/chat/${roomName}/`);
}