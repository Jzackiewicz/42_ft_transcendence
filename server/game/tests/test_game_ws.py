from django.test import TransactionTestCase, Client
from django.contrib.auth import get_user_model
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack

from game.routing import websocket_urlpatterns
from game.models import GameSession, SessionPlayer, Question, SessionQuestion
from game.services.game_flow.game_action_handler import GameAction
from channels.db import database_sync_to_async

User = get_user_model()

class GameConsumerTests(TransactionTestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='testuser', 
			password='password',
			email='testuser@test.com'
		)
		self.unjoined_user = User.objects.create_user(
			username="unjoined",
			password="password",
			email="unjoined@test.com"
		)
		self.user2 = User.objects.create_user(
			username="testuser2",
			password="password",
			email="testuser2@test.com"
		)
		
		self.session = GameSession.objects.create(current_status=GameSession.Status.LOBBY)
		self.player = SessionPlayer.objects.create(
			session=self.session,
			user=self.user,
			display_name="Test User",
			seat_number=1
		)
		self.player2 = SessionPlayer.objects.create(
			session=self.session,
			user=self.user2,
			display_name="Player 2",
			seat_number=2
		)
		
		self.q1 = Question.objects.create(question_text="Test?", correct_answer="yes")
		SessionQuestion.objects.create(session=self.session, question=self.q1, order_index=0)
		
		self.client = Client()
		self.client.force_login(self.user)
		self.cookie = self.client.cookies.get('sessionid').value
		
		self.client2 = Client()
		self.client2.force_login(self.user2)
		self.cookie2 = self.client2.cookies.get('sessionid').value
		
		self.unjoined_client = Client()
		self.unjoined_client.force_login(self.unjoined_user)
		self.unjoined_cookie = self.unjoined_client.cookies.get('sessionid').value

		self.application = AuthMiddlewareStack(URLRouter(websocket_urlpatterns))

	async def test_connect_success(self):
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		connected, _ = await communicator.connect()
		self.assertTrue(connected)
		await communicator.disconnect()

	async def test_connect_unauthenticated(self):
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/"
		)
		connected, _ = await communicator.connect()
		self.assertFalse(connected)

	async def test_connect_unjoined_user(self):
		headers = [(b'cookie', f'sessionid={self.unjoined_cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		connected, _ = await communicator.connect()
		self.assertFalse(connected)

	async def test_receive_missing_action(self):
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		connected, _ = await communicator.connect()
		self.assertTrue(connected)
		await communicator.send_json_to({"payload": {}})
		response = await communicator.receive_json_from()
		self.assertIn("error", response)
		self.assertEqual(response["error"], "Action is required")
		await communicator.disconnect()

	async def test_receive_invalid_payload_format_returns_error(self):
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		connected, _ = await communicator.connect()
		self.assertTrue(connected)
		
		# Brakuje target_player_id wymaganego przez NominatePlayerPayloadSerializer
		await communicator.send_json_to({
			"action": GameAction.NOMINATE_PLAYER, 
			"payload": {}
		})
		response = await communicator.receive_json_from()
		
		self.assertIn("error", response)
		self.assertIn("target_player_id", response["error"])
		await communicator.disconnect()

	async def test_action_domain_validation_error_returns_error_message(self):
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		await communicator.connect()
		
		# Sesja jest w LOBBY, więc submit_answer rzuci błędem z guardów domeny
		await communicator.send_json_to({
			"action": GameAction.SUBMIT_ANSWER, 
			"payload": {"answer": "yes"}
		})
		response = await communicator.receive_json_from()
		
		self.assertEqual(response["type"], "error")
		self.assertIn("Game session is not in answering state", response["message"])
		await communicator.disconnect()

	async def test_successful_action_broadcasts_state_update(self):
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		await communicator.connect()
		
		await communicator.send_json_to({
			"action": GameAction.START_GAME, 
			"payload": {}
		})
		
		response = await communicator.receive_json_from()
		
		self.assertEqual(response["type"], "game_state_update")
		self.assertEqual(response["action"], GameAction.START_GAME)
		self.assertIn("snapshot", response)
		self.assertEqual(response["snapshot"]["current_status"], GameSession.Status.ANSWERING)
		await communicator.disconnect()

	async def test_answering_state_triggers_automatic_timeout_broadcast(self):
		self.session.answer_time_limit_ms = 100
		await database_sync_to_async(self.session.save)()
		
		headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		communicator = WebsocketCommunicator(
			self.application, 
			f"/ws/game/{self.session.session_uuid}/",
			headers=headers
		)
		await communicator.connect()
		
		await communicator.send_json_to({
			"action": GameAction.START_GAME, 
			"payload": {}
		})
		
		start_response = await communicator.receive_json_from()
		self.assertEqual(start_response["action"], GameAction.START_GAME)
		
		timeout_response = await communicator.receive_json_from(timeout=2.0)
		self.assertEqual(timeout_response["type"], "game_state_update")
		self.assertEqual(timeout_response["action"], "evaluate_timeout")
		self.assertIn(timeout_response["snapshot"]["current_status"], [GameSession.Status.ANSWERING, GameSession.Status.GAME_OVER])
		
		await communicator.disconnect()

	async def test_websocket_disconnect_triggers_disconnect_broadcast_to_others(self):
		headers1 = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
		comm1 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers1
		)
		await comm1.connect()
		
		headers2 = [(b'cookie', f'sessionid={self.cookie2}'.encode('ascii'))]
		comm2 = WebsocketCommunicator(
			self.application, f"/ws/game/{self.session.session_uuid}/", headers=headers2
		)
		await comm2.connect()

		await comm1.send_json_to({"action": GameAction.START_GAME, "payload": {}})
		await comm1.receive_json_from()
		await comm2.receive_json_from()

		await comm1.disconnect()

		disconnect_response = await comm2.receive_json_from(timeout=2.0)
		self.assertEqual(disconnect_response["type"], "game_state_update")
		self.assertEqual(disconnect_response["action"], GameAction.DISCONNECT)
		
		await comm2.disconnect()