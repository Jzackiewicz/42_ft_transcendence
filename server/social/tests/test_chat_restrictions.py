from django.test import TestCase, TransactionTestCase
from django.contrib.auth import (
    get_user_model,
    SESSION_KEY,
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
)
from django.contrib.sessions.backends.db import SessionStore
from channels.testing import WebsocketCommunicator
from channels.auth import AuthMiddlewareStack
from channels.routing import URLRouter
from channels.db import database_sync_to_async
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from social.models import Friendship
from social.routing import websocket_urlpatterns
from account.presence import PresenceRegistry


User = get_user_model()

def _dm_room(a, b) -> str:
    """Canonical DM room name — matches the frontend hook's convention."""
    return f"dm_{min(a.id, b.id)}_{max(a.id, b.id)}"


def _make_friends(a, b):
    """Create the two Friendship rows used by services.accept_friend_request."""
    Friendship.objects.create(user=a, friend=b)
    Friendship.objects.create(user=b, friend=a)


def _create_user(username: str) -> User:
    return User.objects.create_user(
        username=username, email=f"{username}@x.com", password="pw-1234-aaaa",
    )


APPLICATION = AuthMiddlewareStack(URLRouter(websocket_urlpatterns))


async def _make_auth_communicator(user, path):
    """Build a WebsocketCommunicator authenticated as user."""
    session = SessionStore()
    session[SESSION_KEY] = str(user.pk)
    session[BACKEND_SESSION_KEY] = "django.contrib.auth.backends.ModelBackend"
    session[HASH_SESSION_KEY] = user.get_session_auth_hash()
    await database_sync_to_async(session.save)()
    headers = [(b"cookie", f"sessionid={session.session_key}".encode())]
    return WebsocketCommunicator(APPLICATION, path, headers=headers)


class ChatHistoryRestrictionTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.alice = _create_user("alice")
        cls.bob = _create_user("bob")
        cls.eve = _create_user("eve")
        _make_friends(cls.alice, cls.bob)

    def _history_url(self, a, b) -> str:
        return f"/api/social/chat/{_dm_room(a, b)}/history/"

    def test_anonymous_request_is_denied(self):
        """No session -> 401/403, never 200 with leaked history."""
        client = APIClient()
        response = client.get(self._history_url(self.alice, self.bob))
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_non_friend_gets_403(self):
        """Eve is friends with neither Alice nor Bob — must be denied."""
        self.client.force_authenticate(self.eve)
        response = self.client.get(self._history_url(self.alice, self.bob))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_friend_in_the_room_gets_200(self):
        """Alice can read her own conversation with Bob."""
        self.client.force_authenticate(self.alice)
        response = self.client.get(self._history_url(self.alice, self.bob))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_malformed_dm_room_is_denied(self):
        """A room name that isn't a parseable DM or 'presence' → 403."""
        self.client.force_authenticate(self.alice)
        response = self.client.get("/api/social/chat/totally_bogus/history/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ChatWsRestrictionTests(TransactionTestCase):

    def setUp(self):
        PresenceRegistry._connections.clear()
        self.alice = _create_user("alice")
        self.bob = _create_user("bob")
        self.eve = _create_user("eve")
        _make_friends(self.alice, self.bob)

    async def test_non_friend_cannot_connect(self):
        path = f"/ws/chat/{_dm_room(self.alice, self.bob)}/"
        communicator = await _make_auth_communicator(self.eve, path)

        connected, _ = await communicator.connect()
        self.assertTrue(connected)   # accept() always runs before close()

        message = await communicator.receive_output()
        self.assertEqual(message["type"], "websocket.close")
        self.assertEqual(message["code"], 4003)

        await communicator.disconnect()

    async def test_friend_can_connect(self):
        """Alice connecting to her own DM room with Bob succeeds."""
        path = f"/ws/chat/{_dm_room(self.alice, self.bob)}/"
        communicator = await _make_auth_communicator(self.alice, path)

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        msg = await communicator.receive_json_from()
        self.assertEqual(msg.get("type"), "presence.update")

        await communicator.disconnect()

    async def test_presence_room_is_exempt(self):
        communicator = await _make_auth_communicator(self.eve, "/ws/chat/presence/")

        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        msg = await communicator.receive_json_from()
        self.assertEqual(msg.get("type"), "presence.update")

        await communicator.disconnect()

    async def test_send_after_unfriend_closes_with_4003(self):
        path = f"/ws/chat/{_dm_room(self.alice, self.bob)}/"
        communicator = await _make_auth_communicator(self.alice, path)
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.receive_json_from()

        await database_sync_to_async(Friendship.objects.filter(
            user=self.alice, friend=self.bob
        ).delete)()
        await database_sync_to_async(Friendship.objects.filter(
            user=self.bob, friend=self.alice
        ).delete)()

        await communicator.send_json_to({"message": "should be blocked"})

        error_msg = await communicator.receive_json_from()
        self.assertIn("error", error_msg)

        close_frame = await communicator.receive_output()
        self.assertEqual(close_frame["type"], "websocket.close")
        self.assertEqual(close_frame["code"], 4003)

        await communicator.disconnect()
