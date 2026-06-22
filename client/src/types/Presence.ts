export interface PresenceUpdateMessage {
	type: 'presence.update'
	user_id: number
	is_online: boolean
}