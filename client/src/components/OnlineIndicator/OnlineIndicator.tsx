import { usePresence } from '../../context/PresenceContext'
import { cx } from '../../utils/cx'
import styles from './OnlineIndicator.module.css'

interface Props {
	userId: number
}

export function OnlineIndicator({ userId }: Props) {
	const { isOnline } = usePresence()
	const online = isOnline(userId)

	return (
		<span
			className={cx(styles.presenceDot, online ? styles.online : styles.offline)}
			role="status"
			aria-label={online ? 'online' : 'offline'}
			title={online ? 'Online' : 'Offline'}
		/>
	)
}