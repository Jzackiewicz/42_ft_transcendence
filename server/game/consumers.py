import asyncio
from datetime import datetime
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError
from .services.game_flow.game_action_handler import GameActionHandler, GameActionRequest, GameAction
from .selectors.lobby_selectors import verify_player_in_session
from .selectors.game_flow_selectors import get_game_snapshot
from .serializers import SubmitAnswerPayloadSerializer, NominatePlayerPayloadSerializer
from .models import GameSession

class GameConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		self.session_uuid = self.scope['url_route']['kwargs']['session_uuid']
		
		self.session_id = await database_sync_to_async(verify_player_in_session)(
			session_uuid=self.session_uuid, 
			user=self.scope['user']
		)
		
		if not self.session_id:
			await self.close()
			return
			
		self.room_group_name = f'game_{self.session_id}'

		await self.channel_layer.group_add(
			self.room_group_name,
			self.channel_name
		)
		await self.accept()
		
		snapshot = await database_sync_to_async(get_game_snapshot)(self.session_id)
		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'game_state_update',
				'action': 'player_connected',
				'snapshot': snapshot
			}
		)

	async def disconnect(self, close_code):
		if hasattr(self, 'room_group_name'):
			await self.channel_layer.group_discard(
				self.room_group_name,
				self.channel_name
			)
			
		if hasattr(self, 'session_id'):
			try:
				request = GameActionRequest(
					session_id=self.session_id,
					action=GameAction.DISCONNECT,
					user=self.scope['user']
				)
				handler = GameActionHandler()
				result = await database_sync_to_async(handler.handle_action)(request)

				if result.session_deleted:
					return

				snapshot = await database_sync_to_async(get_game_snapshot)(self.session_id)
				await self.channel_layer.group_send(
					self.room_group_name,
					{
						'type': 'game_state_update',
						'action': result.action,
						'snapshot': snapshot
					}
				)
			except ValidationError:
				pass

	async def receive_json(self, content):
		action = content.get('action')
		payload = content.get('payload', {})

		if not action:
			await self.send_json({'error': 'Action is required'})
			return

		if action == GameAction.SUBMIT_ANSWER:
			input_serializer = SubmitAnswerPayloadSerializer(data=payload)
			if not input_serializer.is_valid():
				await self.send_json({'error': input_serializer.errors})
				return
			payload = input_serializer.validated_data
		elif action == GameAction.NOMINATE_PLAYER:
			input_serializer = NominatePlayerPayloadSerializer(data=payload)
			if not input_serializer.is_valid():
				await self.send_json({'error': input_serializer.errors})
				return
			payload = input_serializer.validated_data

		try:
			request = GameActionRequest(
				session_id=self.session_id,
				action=action,
				user=self.scope['user'],
				payload=payload
			)
			
			handler = GameActionHandler()
			result = await database_sync_to_async(handler.handle_action)(request)

			snapshot = await database_sync_to_async(get_game_snapshot)(self.session_id)
			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'game_state_update',
					'action': result.action,
					'snapshot': snapshot
				}
			)
		except ValidationError as e:
			await self.send_json({
				'type': 'error',
				'message': e.message if hasattr(e, 'message') else list(e.messages)
			})

	async def game_state_update(self, event):
		snapshot = event['snapshot']
		await self.send_json({
			'type': 'game_state_update',
			'action': event['action'],
			'snapshot': snapshot
		})

		current_status = snapshot.get('current_status')
		if current_status == GameSession.Status.ANSWERING:
			self._schedule_timeout(snapshot)
		else:
			self._cancel_timeout()

	def _schedule_timeout(self, snapshot):
		attempt_id = snapshot.get('current_attempt')
		deadline_at = snapshot.get('turn_deadline_at')

		if not attempt_id or not deadline_at:
			self._cancel_timeout()
			return

		current_attempt_id = getattr(self, 'timeout_attempt_id', None)
		timeout_task = getattr(self, 'timeout_task', None)
		if current_attempt_id == attempt_id and timeout_task and not timeout_task.done():
			return

		self._cancel_timeout()
		self.timeout_attempt_id = attempt_id
		self.timeout_task = asyncio.create_task(
			self._force_timeout(attempt_id, deadline_at)
		)

	def _cancel_timeout(self):
		timeout_task = getattr(self, 'timeout_task', None)
		if timeout_task and not timeout_task.done():
			timeout_task.cancel()
		self.timeout_attempt_id = None

	async def _force_timeout(self, attempt_id, deadline_at):
		deadline = datetime.fromisoformat(deadline_at)
		now = datetime.now(deadline.tzinfo) if deadline.tzinfo else datetime.now()
		sleep_seconds = max((deadline - now).total_seconds(), 0)

		await asyncio.sleep(sleep_seconds + 0.05)
		
		try:
			is_current_attempt = await database_sync_to_async(
				lambda sid, aid: GameSession.objects.filter(
					id=sid,
					current_attempt_id=aid,
					current_status=GameSession.Status.ANSWERING,
				).exists()
			)(self.session_id, attempt_id)
			if not is_current_attempt:
				return

			handler = GameActionHandler()
			result = await database_sync_to_async(handler.handle_timeout)(self.session_id)

			snapshot = await database_sync_to_async(get_game_snapshot)(self.session_id)
			await self.channel_layer.group_send(
				self.room_group_name,
				{
					'type': 'game_state_update',
					'action': result.action,
					'snapshot': snapshot
				}
			)
		except ValidationError:
			pass
