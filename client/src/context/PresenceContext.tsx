import {
	createContext,
	useContext,
	useEffect,
	useRef,
	useState,
	useCallback,
} from 'react'
import { useUser } from './UserContext'
import { PresenceUpdateMessage } from '../types/Presence'

// --- Config -----------------------------------------------------------------

const PRESENCE_ROOM = 'presence'
const RECONNECT_SCHEDULE_MS = [1000, 2000, 4000, 8000, 16000, 30000]

// --- Context shape ----------------------------------------------------------

interface PresenceContextType {
	isOnline: (userId: number) => boolean
	seed: (users: Array<{ id: number; is_online: boolean }>) => void
}

const PresenceContext = createContext<PresenceContextType | null>(null)

// --- Provider ---------------------------------------------------------------

export function PresenceProvider({ children }: { children: React.ReactNode }) {
	const { user, setUser, setActiveSessionUuid } = useUser()

	const [onlineUserIds, setOnlineUserIds] = useState<Set<number>>(new Set())

	const wsRef = useRef<WebSocket | null>(null)
	const reconnectAttemptRef = useRef(0)
	const reconnectTimerRef = useRef<number | null>(null)
	const manuallyClosedRef = useRef(false)

	// --- Helpers ------------------------------------------------------------

	const applyPresenceUpdate = useCallback((userId: number, online: boolean) => {
		setOnlineUserIds(prev => {
			const next = new Set(prev)
			if (online) next.add(userId)
			else next.delete(userId)
			return next
		})
	}, [])

	const seed = useCallback(
		(users: Array<{ id: number; is_online: boolean }>) => {
			setOnlineUserIds(prev => {
				const next = new Set(prev)
				for (const u of users) {
					if (u.is_online) next.add(u.id)
					else next.delete(u.id)
				}
				return next
			})
		},
		[],
	)

	const isOnline = useCallback(
		(userId: number) => onlineUserIds.has(userId),
		[onlineUserIds],
	)

	// --- Connect / disconnect lifecycle -------------------------------------

	const connect = useCallback(() => {
		if (wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
			return
		}

		const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
		const url = `${proto}//${window.location.host}/ws/chat/${PRESENCE_ROOM}/`
		const ws = new WebSocket(url)
		wsRef.current = ws

		ws.onopen = () => {
			reconnectAttemptRef.current = 0
		}

		ws.onmessage = event => {
			let data: unknown
			try {
				data = JSON.parse(event.data)
			} catch {
				return
			}
			if (
				typeof data === 'object' &&
				data !== null &&
				(data as PresenceUpdateMessage).type === 'presence.update'
			) {
				const msg = data as PresenceUpdateMessage
				applyPresenceUpdate(msg.user_id, msg.is_online)
			}
		}

		ws.onerror = err => {
			console.warn('[presence] WS error', err)
		}

		ws.onclose = event => {
			wsRef.current = null

			// 4001 = server rejected because the session is invalid.
			// Reset auth so NavGuards route back to /login.
			if (event.code === 4001) {
				setUser(null)
				setActiveSessionUuid(null)
				return
			}

			if (manuallyClosedRef.current) return

			const idx = Math.min(
				reconnectAttemptRef.current,
				RECONNECT_SCHEDULE_MS.length - 1,
			)
			const delay = RECONNECT_SCHEDULE_MS[idx]
			reconnectAttemptRef.current += 1

			reconnectTimerRef.current = window.setTimeout(() => {
				reconnectTimerRef.current = null
				connect()
			}, delay)
		}
	}, [applyPresenceUpdate, setUser, setActiveSessionUuid])

	const disconnect = useCallback(() => {
		manuallyClosedRef.current = true
		if (reconnectTimerRef.current !== null) {
			clearTimeout(reconnectTimerRef.current)
			reconnectTimerRef.current = null
		}
		if (wsRef.current) {
			wsRef.current.close(1000, 'logout')
			wsRef.current = null
		}
		setOnlineUserIds(new Set())
	}, [])

	// --- Effects: tie connection to auth state ------------------------------

	useEffect(() => {
		if (user === undefined) return       // UserContext still resolving
		if (user === null) {                  // logged out
			disconnect()
			return
		}
		manuallyClosedRef.current = false
		connect()

		return () => {
			manuallyClosedRef.current = true
			if (reconnectTimerRef.current !== null) {
				clearTimeout(reconnectTimerRef.current)
				reconnectTimerRef.current = null
			}
			if (wsRef.current) {
				wsRef.current.close(1000, 'unmount')
				wsRef.current = null
			}
		}
	}, [user, connect, disconnect])

	// Reconnect immediately when the tab becomes visible after being hidden.
	useEffect(() => {
		const onVisibility = () => {
			if (
				document.visibilityState === 'visible' &&
				user &&
				(!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED)
			) {
				if (reconnectTimerRef.current !== null) {
					clearTimeout(reconnectTimerRef.current)
					reconnectTimerRef.current = null
				}
				reconnectAttemptRef.current = 0
				connect()
			}
		}
		document.addEventListener('visibilitychange', onVisibility)
		return () => document.removeEventListener('visibilitychange', onVisibility)
	}, [user, connect])

	return (
		<PresenceContext.Provider value={{ isOnline, seed }}>
			{children}
		</PresenceContext.Provider>
	)
}

// --- Consumer hook ----------------------------------------------------------

export function usePresence() {
	const ctx = useContext(PresenceContext)
	if (!ctx) {
		throw new Error('usePresence must be used inside PresenceProvider')
	}
	return ctx
}