from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model, SESSION_KEY, BACKEND_SESSION_KEY, HASH_SESSION_KEY
from django.contrib.sessions.backends.db import SessionStore
from channels.testing import WebsocketCommunicator
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from channels.db import database_sync_to_async
from social.routing import websocket_urlpatterns
from social.models import ChatMessage
from rest_framework.test import APIClient

User = get_user_model()

# Reuse a single application instance across all WS tests.
# AllowedHostsOriginValidator is intentionally omitted here — it checks the
# Origin header against ALLOWED_HOSTS, which is not configured in the test
# environment and would reject every connection before auth even runs.
# The real ASGI stack in asgi.py includes it; that behaviour is covered by
# integration/staging tests.
APPLICATION = AuthMiddlewareStack(URLRouter(websocket_urlpatterns))

from social.presence import PresenceRegistry


async def _drain_initial_presence(communicator):
    """
    Every authenticated connect() broadcasts a presence.update to the
    'presence' group, which the connecting consumer is part of — so the very
    first message a freshly-connected test client receives is its own
    'I'm online' event. Drain it before asserting on subsequent traffic.
    """
    msg = await communicator.receive_json_from()
    assert msg.get("type") == "presence.update", f"expected presence.update, got {msg}"
    assert msg["user_id"] is not None
    assert msg["is_online"] is True


async def _make_auth_communicator(user, path="/ws/chat/test_room/"):
    """
    Build a WebsocketCommunicator that carries a valid Django session cookie
    for `user`.

    AuthMiddlewareStack uses Django's SessionMiddleware under the hood, so
    creating a real SessionStore entry and passing its key as the `sessionid`
    cookie is the correct way to authenticate a WebSocket in tests — the same
    path the browser takes in production.
    """
    session = SessionStore()
    session[SESSION_KEY] = str(user.pk)
    session[BACKEND_SESSION_KEY] = "django.contrib.auth.backends.ModelBackend"
    session[HASH_SESSION_KEY] = user.get_session_auth_hash()
    await database_sync_to_async(session.save)()
    headers = [(b"cookie", f"sessionid={session.session_key}".encode())]
    return WebsocketCommunicator(APPLICATION, path, headers=headers)


# ---------------------------------------------------------------------------
# Authentication enforcement
# ---------------------------------------------------------------------------

class ChatAuthTests(TransactionTestCase):
    """Verify that ChatConsumer enforces authentication at connect time."""

    def setUp(self):
        # In-memory registry is process-global; clear between tests so state
        # from one test doesn't leak into the next.
        PresenceRegistry._connections.clear()

    async def test_anonymous_connection_closed_with_4001(self):
        """
        A connection with no session cookie must be accepted at the protocol
        level (the WS handshake must complete before a close frame can be
        sent) and then immediately closed with code 4001.

        Clients should treat 4001 as 'not authenticated' and redirect to login.
        """
        communicator = WebsocketCommunicator(APPLICATION, "/ws/chat/test_room/")

        connected, _ = await communicator.connect()
        # The server calls accept() before close() — so connected is True here.
        self.assertTrue(connected)

        # The very next message from the server must be a close frame with code 4001.
        message = await communicator.receive_output()
        self.assertEqual(message["type"], "websocket.close")
        self.assertEqual(message["code"], 4001)

        await communicator.disconnect()

    async def test_authenticated_connection_accepted(self):
        """A user with a valid session should connect without being closed."""
        user = await database_sync_to_async(User.objects.create_user)(
            username="alice", password="s3cr3t"
        )
        communicator = await _make_auth_communicator(user)

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # The presence feature emits one presence.update on connect; drain it
        # before asserting that no further unsolicited messages arrive.
        await _drain_initial_presence(communicator)
        self.assertTrue(await communicator.receive_nothing())

        await communicator.disconnect()

    async def test_broadcast_carries_real_username(self):
        """
        The sender_username field in every broadcast must be the authenticated
        user's actual username — never a placeholder like 'Mr. Player'.
        """
        user = await database_sync_to_async(User.objects.create_user)(
            username="alice", password="s3cr3t"
        )
        communicator = await _make_auth_communicator(user)
        await communicator.connect()
        await _drain_initial_presence(communicator)

        await communicator.send_json_to({"message": "hello room"})
        response = await communicator.receive_json_from()

        self.assertEqual(response["sender_username"], "alice")
        self.assertEqual(response["message"], "hello room")
        self.assertIn("timestamp", response)

        await communicator.disconnect()


# ---------------------------------------------------------------------------
# Functional / message validation tests (require authenticated user)
# ---------------------------------------------------------------------------

class ChatConsumerTests(TransactionTestCase):
    """
    Tests for ChatConsumer message handling.

    Uses TransactionTestCase (not TestCase) because database_sync_to_async
    runs DB operations on a worker thread. TestCase wraps each test in a
    transaction on the main thread's connection; the worker thread can't
    share it and gets a closed connection. TransactionTestCase commits for
    real, so worker threads can see the data.

    All connections are authenticated — an unauthenticated communicator would
    be rejected before any message handling runs.
    """

    def setUp(self):
        # Sync setUp is required — Django's test runner calls setUp() without
        # await even when test methods are async. Since this runs on the main
        # thread (not a worker), a plain ORM call works fine here.
        PresenceRegistry._connections.clear()
        self.user = User.objects.create_user(username="testuser", password="pass")

    async def _communicator(self, path="/ws/chat/test_room/"):
        return await _make_auth_communicator(self.user, path)

    async def test_valid_message_broadcast(self):
        """A well-formed message is echoed back with username and timestamp."""
        communicator = await self._communicator()
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await _drain_initial_presence(communicator)

        await communicator.send_json_to({"message": "Halo halo dupa123!"})
        response = await communicator.receive_json_from()

        self.assertEqual(response["message"], "Halo halo dupa123!")
        self.assertEqual(response["sender_username"], "testuser")
        self.assertIn("timestamp", response)

        await communicator.disconnect()

    async def test_invalid_message_key(self):
        """Missing 'message' key returns an error payload, connection stays open."""
        communicator = await self._communicator()
        await communicator.connect()
        await _drain_initial_presence(communicator)

        await communicator.send_json_to({"bad_key": "Failed"})

    async def test_message_too_long(self):
        """Messages exceeding 500 characters return a validation error."""
        communicator = await self._communicator()
        await communicator.connect()
        await _drain_initial_presence(communicator)

        await communicator.send_json_to({"message": "A" * 501})


# ---------------------------------------------------------------------------
# Chat history REST API tests (unchanged, kept here for co-location)
# ---------------------------------------------------------------------------

class ChatHistoryAPITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.room_name = "test_lobby"

        ChatMessage.objects.create(
            room_name=self.room_name,
            sender_username="Alice",
            message="Pierwsza wiadomość",
        )
        ChatMessage.objects.create(
            room_name=self.room_name,
            sender_username="Bob",
            message="Druga wiadomość",
        )

    def test_get_chat_history_returns_200_and_data(self):
        """Getting chat history returns 200 OK with the stored messages."""
        response = self.client.get(f"/api/social/chat/{self.room_name}/history/")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["sender_username"], "Alice")
        self.assertEqual(data[1]["message"], "Druga wiadomość")

    def test_get_chat_history_pagination_limit(self):
        """Endpoint caps at 50 messages regardless of how many exist."""
        for i in range(55):
            ChatMessage.objects.create(
                room_name=self.room_name,
                sender_username="Spammer",
                message=f"Spam message {i}",
            )

        response = self.client.get(f"/api/social/chat/{self.room_name}/history/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 50)
