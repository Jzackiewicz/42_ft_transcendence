import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.accept()
            await self.close(code=4001)
            return
        
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': f'Connected as {user.username}'
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', 'No message')

            await self.send(text_data=json.dumps({
                'message': f'Server received: {message}',
                'sender_username': self.scope["user"].username,
            }))
