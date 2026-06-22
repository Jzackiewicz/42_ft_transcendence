import { apiClient } from './apiClient';

export async function createLobby() {
    const res = await apiClient.post('/game/lobby/create/');
    return res.data;
}

export async function getUserStats(userId: number) {
    const res = await apiClient.get(`/game/users/${userId}/stats/`);
    return res.data;
}

export async function joinLobby(joinUuid: string) {
    await apiClient.post(`/game/lobby/join/${joinUuid}/`);
}

// skipGlobalErrorRedirect: a failed LLM call returns 502, which we want to
// surface inline in the lobby instead of triggering the global /error redirect.
export async function generateExtraQuestions(sessionUuid: string) {
    const res = await apiClient.post(
        '/game/generate_extra_questions/',
        { session_uuid: sessionUuid },
        { skipGlobalErrorRedirect: true } as any,
    );
    return res.data;
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