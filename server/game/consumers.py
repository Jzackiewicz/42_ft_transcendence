import json
from channels.generic.websocket import AsyncWebsocketConsumer

class EchoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            'message': 'Client connected!'
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            # When the frontend sends us a message
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', 'No message')

            # Send it back (Echo)
            await self.send(text_data=json.dumps({
                'message': f'Server received: {message}'
            }))