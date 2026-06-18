import { usePresence } from '../context/PresenceContext'
import './OnlineIndicator.css'

interface Props {
	userId: number
}

export function OnlineIndicator({ userId }: Props) {
	const { isOnline } = usePresence()
	const online = isOnline(userId)

	return (
		<span
			className={`presence-dot ${online ? 'online' : 'offline'}`}
			role="status"
			aria-label={online ? 'online' : 'offline'}
			title={online ? 'Online' : 'Offline'}
		/>
	)
}