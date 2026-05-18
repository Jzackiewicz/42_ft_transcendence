const BASE = '' // for now leave empty
// const BASE = import.meta.env.VITE_API_URL

function getCSRFToken(): string {
  const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))
  return cookie ? cookie.split('=')[1] : ''
}

export async function register(username: string, email: string, password: string) {
    const res = await fetch(`${BASE}/account/users/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
        credentials: 'include',
        body: JSON.stringify({ username, email, password })
    })
    if (!res.ok) { 
        const err = await res.json()
        throw new Error(JSON.stringify(err))
    }
    return res.json()
}

export async function login(username: string, password: string) {
    console.log("Sending login request:", { username, password })
    const res = await fetch(`${BASE}/account/users/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
        credentials: 'include',
        body: JSON.stringify({ username, password })
    })
    console.log("Login response:", res)
    if (!res.ok) {
        const text = await res.text()
        throw new Error(text || `HTTP error ${res.status}`)
    }
    return res.json()
}


export async function logout() {
    const res = await fetch(`${BASE}/account/users/logout/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCSRFToken() },
        credentials: 'include',
    })
    if (!res.ok) {
        const err = await res.json()
        throw new Error(JSON.stringify(err))
    }
}

export async function getUser(userId: number) {
    const res = await fetch(`${BASE}/account/users/${userId}/`, {
        method: 'GET',
        credentials: 'include'
    })
    if (!res.ok) {
        const err = await res.json()
        throw new Error(JSON.stringify(err))
    }
    return res.json()
}

export async function getMe() {
    const res = await fetch(`${BASE}/account/users/me/`, {
        credentials: 'include'
    })
    if (!res.ok) {
        return null
    }
    return res.json()
}

// ws: — plain WebSocket (like http://)
// wss: — secure WebSocket (like https://)
export function connectGameSocket(): WebSocket {
  return new WebSocket(`ws://localhost:5173/ws/game/`)
}

export function connectChatSocket(roomName: string): WebSocket {
  return new WebSocket(`ws://localhost:5173/ws/chat/${roomName}/`)
}