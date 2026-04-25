const BASE = ''//import.meta.env.VITE_API_URL

function getCsrfToken(): string {
  const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='))
  return cookie ? cookie.split('=')[1] : ''
}

export async function initCsrf() {
  await fetch(`${BASE}/account/users/`, { credentials: 'include' })
}

export async function register(username: string, email: string, password: string) {
    const res = await fetch(`${BASE}/account/users/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        credentials: 'include',
        body: JSON.stringify({ username, email, password })
    })
    if (!res.ok) { 
        const err = await res.json()
        throw new Error(JSON.stringify(err))
    }
    return res.json()
}

export async function login(username: string, email:string, password: string) {
    const res = await fetch(`${BASE}/account/users/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        credentials: 'include',
        body: JSON.stringify({ username, email, password })
    })
    if (!res.ok) { 
        const err = await res.json()
        throw new Error(JSON.stringify(err))
    }
    return res.json()
}


export async function logout() {
    const res = await fetch(`${BASE}/account/users/logout/`, {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrfToken() },
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