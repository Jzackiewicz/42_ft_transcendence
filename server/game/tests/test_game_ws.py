from django.test import TransactionTestCase, Client
from django.contrib.auth import get_user_model
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

from game.routing import websocket_urlpatterns
from game.models import GameSession, SessionPlayer

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
		
		self.session = GameSession.objects.create(current_status=GameSession.Status.LOBBY)
		self.player = SessionPlayer.objects.create(
			session=self.session,
			user=self.user,
			display_name="Test User",
			seat_number=1
		)
		
		self.client = Client()
		self.client.force_login(self.user)
		self.cookie = self.client.cookies.get('sessionid').value
		
		self.unjoined_client = Client()
		self.unjoined_client.force_login(self.unjoined_user)
		self.unjoined_cookie = self.unjoined_client.cookies.get('sessionid').value

		self.application = AllowedHostsOriginValidator(
			AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
		)

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