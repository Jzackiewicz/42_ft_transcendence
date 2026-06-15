from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from channels.routing import URLRouter
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
    SESSION_KEY,
    get_user_model,
)
from django.contrib.sessions.backends.db import SessionStore
from django.test import TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIClient

from account.presence import PresenceRegistry
from social.models import Friendship
from social.routing import websocket_urlpatterns

User = get_user_model()

APPLICATION = AuthMiddlewareStack(URLRouter(websocket_urlpatterns))


async def _make_auth_communicator(user, path="/ws/chat/test_room/"):
    """Mirror of the helper in test_chat_ws.py — builds a session cookie the
    AuthMiddlewareStack will accept. Duplicated here on purpose so the
    presence test can run independently of the chat-WS test module."""
    from channels.testing import WebsocketCommunicator

    session = SessionStore()
    session[SESSION_KEY] = str(user.pk)
    session[BACKEND_SESSION_KEY] = "django.contrib.auth.backends.ModelBackend"
    session[HASH_SESSION_KEY] = user.get_session_auth_hash()
    await database_sync_to_async(session.save)()
    headers = [(b"cookie", f"sessionid={session.session_key}".encode())]
    return WebsocketCommunicator(APPLICATION, path, headers=headers)


async def _drain_initial_presence(communicator):
    """The just-connected consumer is itself in PRESENCE_GROUP, so its own
    'I'm online' broadcast is the first message it receives. Drain it before
    the test body uses the communicator for anything else."""
    msg = await communicator.receive_json_from()
    assert msg.get("type") == "presence.update"


class FriendListIsOnlineIntegrationTests(TransactionTestCase):
    """
    Verify /api/social/friends/ reports the friend's live PresenceRegistry
    state, not a stale DB value.
    """

    def setUp(self):
        # In-process registry is module-global; clear it so a previous test's
        # ghost socket doesn't make our friend appear online.
        PresenceRegistry._connections.clear()

        self.password = "pw-1234-aaaa"
        self.alice = User.objects.create_user(
            username="alice", email="alice@example.com", password=self.password
        )
        self.bob = User.objects.create_user(
            username="bob", email="bob@example.com", password=self.password
        )
        # Friendship is stored as two rows (one per direction) — matches the
        # convention used in test_friends.py.
        Friendship.objects.create(user=self.alice, friend=self.bob)
        Friendship.objects.create(user=self.bob, friend=self.alice)

    def _fetch_friends_as_alice(self) -> list[dict]:
        """Sync helper: log in as Alice with APIClient and read her friend list."""
        client = APIClient()
        client.login(username="alice", password=self.password)
        response = client.get(reverse("friend-list"))
        assert response.status_code == 200, response.content
        return response.json()

    async def test_friend_is_online_only_while_their_ws_is_open(self):
        # --- 1. Before Bob connects: he must show offline ----------------
        body = await database_sync_to_async(self._fetch_friends_as_alice)()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["friend"]["username"], "bob")
        self.assertFalse(
            body[0]["friend"]["is_online"],
            "Bob has no WS open yet — must be offline.",
        )

        # --- 2. Bob opens a chat WS: he must show online -----------------
        bob_ws = await _make_auth_communicator(self.bob)
        connected, _ = await bob_ws.connect()
        self.assertTrue(connected)
        # Drain his own connect broadcast so the registry write has landed.
        await _drain_initial_presence(bob_ws)

        body = await database_sync_to_async(self._fetch_friends_as_alice)()
        self.assertTrue(
            body[0]["friend"]["is_online"],
            "Bob's chat WS is open — friend list must report is_online=True.",
        )

        # --- 3. Bob disconnects: he must flip back to offline ------------
        await bob_ws.disconnect()

        body = await database_sync_to_async(self._fetch_friends_as_alice)()
        self.assertFalse(
            body[0]["friend"]["is_online"],
            "Bob disconnected — friend list must report is_online=False.",
        )

    async def test_second_tab_keeps_user_online_after_first_closes(self):
        """
        Regression guard for the multi-tab case: PresenceRegistry stores a
        SET of channels per user, so closing one tab while another is open
        must not mark the user offline.
        """
        tab_one = await _make_auth_communicator(self.bob, path="/ws/chat/r1/")
        tab_two = await _make_auth_communicator(self.bob, path="/ws/chat/r2/")

        await tab_one.connect()
        await _drain_initial_presence(tab_one)
        await tab_two.connect()
        # tab_two does NOT re-broadcast (no transition), but tab_one does
        # receive nothing extra either — both are now in the registry.

        await tab_one.disconnect()

        body = await database_sync_to_async(self._fetch_friends_as_alice)()
        self.assertTrue(
            body[0]["friend"]["is_online"],
            "Closing one of two tabs must leave the user online.",
        )

        await tab_two.disconnect()

        body = await database_sync_to_async(self._fetch_friends_as_alice)()
        self.assertFalse(
            body[0]["friend"]["is_online"],
            "After closing the last tab, the user must flip offline.",
        )
