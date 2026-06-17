from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ValidationError
from .services.game_flow.game_action_handler import GameActionHandler, GameActionRequest, GameAction
from .services.game_flow.timer_manager import GameTimerManager
from .services.game_flow.lifecycle import reconnect_player
from .selectors.lobby_selectors import verify_player_in_session
from .selectors.game_flow_selectors import get_game_snapshot
from .serializers import SubmitAnswerPayloadSerializer, NominatePlayerPayloadSerializer

class GameConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		self.session_uuid = self.scope['url_route']['kwargs']['session_uuid']
		
		self.session_id, self.session_player_id, self.is_spectator = await database_sync_to_async(verify_player_in_session)(
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
		
		await database_sync_to_async(reconnect_player)(self.session_player_id)
		
		handler = GameActionHandler()
		sync_result = await database_sync_to_async(handler.sync_game_disconnections)(self.session_id)
		if sync_result.session_deleted:
			await self.close()
			return

		snapshot = await database_sync_to_async(get_game_snapshot)(self.session_id)
		await self.channel_layer.group_send(
			self.room_group_name,
			{
				'type': 'game_state_update',
				'action': 'player_connected',
				'snapshot': snapshot
			}
		)
		self._schedule_timer(sync_result)

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
					GameTimerManager.cancel(self.session_id)
					return

				sync_result = await database_sync_to_async(handler.sync_game_disconnections)(self.session_id)
				if sync_result.session_deleted:
					GameTimerManager.cancel(self.session_id)
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

				self._schedule_timer(sync_result)
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

			if result.session_deleted:
				GameTimerManager.cancel(self.session_id)
				await self.close()
				return

			sync_result = await database_sync_to_async(handler.sync_game_disconnections)(self.session_id)
			if sync_result.session_deleted:
				GameTimerManager.cancel(self.session_id)
				await self.close()
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

			self._schedule_timer(sync_result)
		except ValidationError as e:
			await self.send_json({
				'type': 'error',
				'message': e.message if hasattr(e, 'message') else list(e.messages)
			})

	async def game_state_update(self, event):
		snapshot = dict(event['snapshot'])
		snapshot['is_spectator'] = self.is_spectator
		await self.send_json({
			'type': 'game_state_update',
			'action': event['action'],
			'your_player_id': self.session_player_id,
			'snapshot': snapshot
		})

	def _schedule_timer(self, result):
		"""Schedule or cancel a timer based on the handler result."""
		if not result.timer_data:
			GameTimerManager.cancel(self.session_id)
			return

		GameTimerManager.schedule(self.session_id, result.timer_data, self.room_group_name)
