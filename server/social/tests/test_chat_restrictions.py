import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from social.models import Friendship

User = get_user_model()


def _dm_room(a, b) -> str:
    return f"dm_{min(a.id, b.id)}_{max(a.id, b.id)}"


def _create_user(username: str) -> User:
    return User.objects.create_user(
        username=username, password="pw", email=f"{username}@x.com",
    )


def _make_friends(a, b):
    Friendship.objects.create(user=a, friend=b)
    Friendship.objects.create(user=b, friend=a)


@pytest.mark.django_db
def test_chat_history_requires_auth():
    """Anonymous request should be rejected (no leaking conversation history)."""
    client = APIClient()
    resp = client.get("/social/chat/dm_1_2/history/")
    assert resp.status_code in (401, 403)


@pytest.mark.django_db
def test_chat_history_forbidden_for_non_friend():
    """Authenticated but not-a-friend -> 403."""
    alice, bob, eve = _create_user("alice"), _create_user("bob"), _create_user("eve")
    _make_friends(alice, bob)

    client = APIClient()
    client.force_authenticate(eve)
    resp = client.get(f"/social/chat/{_dm_room(alice, bob)}/history/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_chat_history_works_for_friend():
    """The two participants can read their own conversation."""
    alice, bob = _create_user("alice"), _create_user("bob")
    _make_friends(alice, bob)

    client = APIClient()
    client.force_authenticate(alice)
    resp = client.get(f"/social/chat/{_dm_room(alice, bob)}/history/")
    assert resp.status_code == 200


@pytest.mark.django_db
def test_chat_history_rejects_malformed_room_name():
    """Non-DM room names that aren't 'presence' should be denied."""
    alice = _create_user("alice")

    client = APIClient()
    client.force_authenticate(alice)
    resp = client.get("/social/chat/totally_bogus/history/")
    assert resp.status_code == 403