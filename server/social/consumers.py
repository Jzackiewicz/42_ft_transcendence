import datetime
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .serializers import ChatMessageSerializer

class ChatConsumer(AsyncJsonWebsocketConsumer):
		#TODO: add authentication (JWT token) and get the username from the token
		async def connect(self):
				self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
				self.room_group_name = f"chat_{self.room_name}"

				await self.channel_layer.group_add(self.room_group_name, self.channel_name)
				await self.accept()

		# Remember to manually close possible future processes
		async def disconnect(self, close_code):
				await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

		# Receive message from WebSocket
		async def receive_json(self, content, **kwargs):

				input_serializer = ChatMessageSerializer(data=content)
				if not input_serializer.is_valid():
						await self.send_json({
							"error": "Invalid message format.",
							"details": input_serializer.errors
						})
						return

				message = input_serializer.validated_data["message"]

				# TODO: get sender's username from the scope (JWT token)
				await self.channel_layer.group_send(
						self.room_group_name,
						{
								"type": "chat_message",
								"message": message,
								"sender_username": "Mr. Player",
								"timestamp": datetime.datetime.now().isoformat(),
						},
				)

		async def chat_message(self, event):
				message = event["message"]
				sender_username = event["sender_username"]
				timestamp = event["timestamp"]
				await self.send_json({
						"message": message,
						"sender_username": sender_username,
						"timestamp": timestamp,
				})
