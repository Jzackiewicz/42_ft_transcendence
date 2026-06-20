from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

GAME_STATE_UPDATE = "game_state_update"


def _game_group_name(session_id) -> str:
	return f"game_{session_id}"


def _snapshot_event(action, snapshot) -> dict:
	return {
		"type": GAME_STATE_UPDATE,
		"action": action,
		"snapshot": snapshot,
	}


async def broadcast_snapshot(session_id, action, snapshot) -> None:
	"""Broadcast a snapshot from async code"""
	channel_layer = get_channel_layer()
	await channel_layer.group_send(
		_game_group_name(session_id),
		_snapshot_event(action, snapshot),
	)


def broadcast_snapshot_sync(session_id, action, snapshot) -> None:
	"""Broadcast a snapshot from synchronous code"""
	channel_layer = get_channel_layer()
	async_to_sync(channel_layer.group_send)(
		_game_group_name(session_id),
		_snapshot_event(action, snapshot),
	)
