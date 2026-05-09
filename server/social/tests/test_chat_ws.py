from django.test import TestCase
from channels.testing import WebsocketCommunicator
from social.routing import websocket_urlpatterns
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from social.models import ChatMessage
from rest_framework.test import APIClient


class ChatTests(TestCase):
	async def test_chat_consumer(self):
		""""Correct use of the endpoint"""
		application = AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
		communicator = WebsocketCommunicator(application, "/ws/chat/test_room/")

		connected, subprotocol = await communicator.connect()
		self.assertTrue(connected)

		await communicator.send_json_to({"message": "Halo halo dupa123!"})

		response = await communicator.receive_json_from()
		self.assertEqual(response["message"], "Halo halo dupa123!")
		self.assertEqual(response["sender_username"], "Mr. Player")
		self.assertIn("timestamp", response, "No timestamp!")
		await communicator.disconnect()

	async def test_chat_consumer_invalid_input(self):
		"""Incorrect use of the endpoint - missing 'message' key"""
		application = AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
		communicator = WebsocketCommunicator(application, "/ws/chat/test_room/")
		
		await communicator.connect()

		await communicator.send_json_to({"bad_key": "Failed"})

		response = await communicator.receive_json_from()
		
		self.assertIn("error", response)
		self.assertEqual(response["error"], "Invalid message format.")
		self.assertIn("details", response)
		
		await communicator.disconnect()
			
	async def test_chat_consumer_message_too_long(self):
		"""Testing limit of 500 characters in message"""
		application = AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
		communicator = WebsocketCommunicator(application, "/ws/chat/test_room/")
		await communicator.connect()

		too_long_message = "A" * 501 
		await communicator.send_json_to({"message": too_long_message})

		response = await communicator.receive_json_from()
		
		self.assertIn("error", response)
		self.assertEqual(response["error"], "Invalid message format.")
		self.assertIn("message", response["details"]) 
		
		await communicator.disconnect()


class ChatHistoryAPITests(TestCase):
	def setUp(self):
		from django.contrib.auth import get_user_model
		User = get_user_model()
		self.user = User.objects.create_user(username='testuser', password='password')
		
		self.client = APIClient()
		self.client.force_authenticate(user=self.user)
		self.room_name = "test_lobby"
		
		ChatMessage.objects.create(
			room_name=self.room_name, 
			sender_username="Alice", 
			message="Pierwsza wiadomość"
		)
		ChatMessage.objects.create(
			room_name=self.room_name, 
			sender_username="Bob", 
			message="Druga wiadomość"
		)

	def test_get_chat_history_returns_200_and_data(self):
		"""Getting chat history and expecting 200 OK """
		response = self.client.get(f'/social/chat/{self.room_name}/history/')
		
		self.assertEqual(response.status_code, 200)
		
		data = response.json()
		self.assertEqual(len(data), 2)
		
		self.assertEqual(data[0]["sender_username"], "Alice")
		self.assertEqual(data[1]["message"], "Druga wiadomość")

	def test_get_chat_history_pagination_limit(self):
		"""Testing if endpoint correctly caps at 50 messages limit"""
		for i in range(55):
			ChatMessage.objects.create(
				room_name=self.room_name, 
				sender_username="Spammer", 
				message=f"Spam message {i}"
			)
			
		response = self.client.get(f'/social/chat/{self.room_name}/history/')
		self.assertEqual(response.status_code, 200)
		
		data = response.json()
		
		self.assertEqual(len(data), 50)
		
