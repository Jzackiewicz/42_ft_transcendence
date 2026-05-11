import asyncio
from channels.testing import WebsocketCommunicator
from django.test import TransactionTestCase, Client
from django.contrib.auth import get_user_model
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter

from game.routing import websocket_urlpatterns
from game.models import GameSession, SessionPlayer, Question, SessionQuestion
from game.services.game_flow.game_action_handler import GameAction

User = get_user_model()

class GameWSAsyncTimeoutTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password', email='testuser@test.com')
        self.user2 = User.objects.create_user(username="testuser2", password="password", email="testuser2@test.com")

        self.session = GameSession.objects.create(current_status=GameSession.Status.LOBBY, answer_time_limit_ms=200)
        self.player = SessionPlayer.objects.create(session=self.session, user=self.user, display_name="Test User", seat_number=1)
        self.player2 = SessionPlayer.objects.create(session=self.session, user=self.user2, display_name="Player 2", seat_number=2)
        self.session.host_player = self.player
        self.session.save()

        self.q1 = Question.objects.create(question_text="Test?", correct_answer="yes")
        self.q2 = Question.objects.create(question_text="Test2?", correct_answer="no")
        SessionQuestion.objects.create(session=self.session, question=self.q1, order_index=0)
        SessionQuestion.objects.create(session=self.session, question=self.q2, order_index=1)

        self.client = Client()
        self.client.force_login(self.user)
        self.cookie = self.client.cookies.get('sessionid').value

        self.application = AuthMiddlewareStack(URLRouter(websocket_urlpatterns))

    async def test_fast_answer_cancels_timeout_task(self):
        headers = [(b'cookie', f'sessionid={self.cookie}'.encode('ascii'))]
        communicator = WebsocketCommunicator(
            self.application, 
            f"/ws/game/{self.session.session_uuid}/",
            headers=headers
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        await communicator.send_json_to({"action": GameAction.START_GAME})
        start_response = await communicator.receive_json_from()
        
        # Immediate wrong answer
        await communicator.send_json_to({
            "action": GameAction.SUBMIT_ANSWER,
            "payload": {"answer_text": "wrong"}
        })

        try:
            while True:
                # We pull from WS until an exception or timeout.
                # If the backend is spitting out evaluate_timeout incorrectly, it'll appear within 500ms
                res = await communicator.receive_json_from(timeout=0.6)
                if res.get("action") == "evaluate_timeout":
                    self.fail("Received evaluate_timeout event despite answering early! Task not cancelled.")
        except asyncio.TimeoutError:
            pass
        except asyncio.CancelledError:
            pass

        try:
            await communicator.disconnect()
        except:
            pass

