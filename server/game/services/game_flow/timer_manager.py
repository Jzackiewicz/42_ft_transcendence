import asyncio
from datetime import datetime, timedelta

from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.core.exceptions import ValidationError

from game.models import GameSession
from game.selectors.game_flow_selectors import get_game_snapshot
from game.services.game_flow.game_action_handler import GameActionHandler


class GameTimerManager:
	"""Manages game timers in memory.

	Works only because we run a single Daphne process.
	With multiple workers, we'd need Redis/Celery for scheduling.
	"""

	_timers: dict[int, asyncio.Task] = {}

	@classmethod
	def schedule(cls, session_id: int, timer_data: dict, room_group_name: str) -> None:
		cls.cancel(session_id)

		deadline_at = timer_data['deadline_at']
		attempt_id = timer_data['attempt_id']
		timer_type = timer_data['type']

		now = datetime.now(deadline_at.tzinfo) if deadline_at.tzinfo else datetime.now()
		sleep_seconds = max((deadline_at - now).total_seconds(), 0)

		if timer_type == 'answer_timeout':
			coro = cls._run_answer_timeout(session_id, attempt_id, sleep_seconds, room_group_name)
		elif timer_type == 'evaluation_finish':
			coro = cls._run_evaluation_finish(session_id, attempt_id, sleep_seconds, room_group_name)
		else:
			return

		cls._timers[session_id] = asyncio.create_task(coro)

	@classmethod
	def cancel(cls, session_id: int) -> None:
		task = cls._timers.pop(session_id, None)
		if task and not task.done():
			task.cancel()

	# Internal coroutines

	@classmethod
	async def _run_answer_timeout(
		cls,
		session_id: int,
		attempt_id: int,
		sleep_seconds: float,
		room_group_name: str,
	) -> None:
		await asyncio.sleep(sleep_seconds + 0.05)
		cls._timers.pop(session_id, None)

		try:
			is_current = await database_sync_to_async(
				lambda: GameSession.objects.filter(
					id=session_id,
					current_attempt_id=attempt_id,
					current_status=GameSession.Status.ANSWERING,
				).exists()
			)()
			if not is_current:
				return

			handler = GameActionHandler()
			result = await database_sync_to_async(handler.handle_timeout)(session_id)

			snapshot = await database_sync_to_async(get_game_snapshot)(session_id)
			channel_layer = get_channel_layer()
			await channel_layer.group_send(
				room_group_name,
				{
					'type': 'game_state_update',
					'action': result.action,
					'snapshot': snapshot,
				}
			)

			cls._schedule_from_result(session_id, result, room_group_name)
		except ValidationError:
			pass

	@classmethod
	async def _run_evaluation_finish(
		cls,
		session_id: int,
		attempt_id: int,
		sleep_seconds: float,
		room_group_name: str,
	) -> None:
		await asyncio.sleep(sleep_seconds + 0.05)
		cls._timers.pop(session_id, None)

		try:
			is_current = await database_sync_to_async(
				lambda: GameSession.objects.filter(
					id=session_id,
					current_attempt_id=attempt_id,
					current_status=GameSession.Status.EVALUATION,
				).exists()
			)()
			if not is_current:
				return

			handler = GameActionHandler()
			result = await database_sync_to_async(handler.handle_evaluation_finish)(session_id)

			snapshot = await database_sync_to_async(get_game_snapshot)(session_id)
			channel_layer = get_channel_layer()
			await channel_layer.group_send(
				room_group_name,
				{
					'type': 'game_state_update',
					'action': result.action,
					'snapshot': snapshot,
				}
			)

			cls._schedule_from_result(session_id, result, room_group_name)
		except ValidationError:
			pass

	@classmethod
	def _schedule_from_result(cls, session_id: int, result, room_group_name: str) -> None:
		"""Chain-schedule the next timer based on the handler result's timer_data."""
		if not result.timer_data:
			return
		cls.schedule(session_id, result.timer_data, room_group_name)
