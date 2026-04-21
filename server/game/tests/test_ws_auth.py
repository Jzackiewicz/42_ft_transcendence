from django.test import TransactionTestCase
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore
from channels.testing import WebsocketCommunicator
from core.asgi import application

User = get_user_model()

class WebSocketAuthenticationTests(TransactionTestCase):
    
    async def test_websocket_authenticated_connection(self):
        user = await User.objects.acreate_user(username='testuser', password='testpassword')
        
        session = SessionStore()
        await session.acreate()
        
        session['_auth_user_id'] = str(user.pk)
        session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
        session['_auth_user_hash'] = user.get_session_auth_hash()
        await session.asave()
        
        headers = [
            (b"origin", b"http://localhost"),
            (b"cookie", f"sessionid={session.session_key}".encode()),
        ]
        
        communicator = WebsocketCommunicator(
            application, 
            "/ws/game/",
            headers=headers
        )
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected, "Connection rejected.")
        
        welcome_response = await communicator.receive_json_from()
        self.assertEqual(welcome_response.get('message'), 'Connected as testuser')
        
        await communicator.send_json_to({'message': 'Test request'})
        echo_response = await communicator.receive_json_from()
        
        self.assertEqual(echo_response.get('message'), 'Server received: Test request')
        self.assertEqual(echo_response.get('sender_username'), 'testuser')
        
        await communicator.disconnect()

    async def test_websocket_unauthenticated_connection(self):
        headers = [
            (b"origin", b"http://localhost"),
        ]
        
        communicator = WebsocketCommunicator(
            application, 
            "/ws/game/",
            headers=headers
        )
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        close_message = await communicator.receive_output(timeout=1)
        self.assertEqual(close_message["type"], "websocket.close")
        self.assertEqual(close_message.get("code"), 4001)

        await communicator.disconnect()