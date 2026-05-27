from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from social.models import Friendship, FriendRequest

User = get_user_model()

PASSWORD = "pw-1234-aaaa"


def _login(client, user):
    client.login(username=user.username, password=PASSWORD)


# ---------------------------------------------------------------------------
# Sending requests
# ---------------------------------------------------------------------------

class SendFriendRequestTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user(
            username="alice", email="alice@example.com", password=PASSWORD
        )
        cls.bob = User.objects.create_user(
            username="bob", email="bob@example.com", password=PASSWORD
        )

    def setUp(self):
        _login(self.client, self.alice)
        self.url = reverse("friend-request-collection")

    def test_send_creates_pending_request(self):
        response = self.client.post(self.url, {"to_user_id": self.bob.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            FriendRequest.objects.filter(
                from_user=self.alice, to_user=self.bob
            ).exists()
        )

        body = response.json()
        self.assertEqual(body["from_user"]["username"], "alice")
        self.assertEqual(body["to_user"]["username"], "bob")

    def test_cannot_send_to_self(self):
        # Serializer-level rejection → 400.
        response = self.client.post(self.url, {"to_user_id": self.alice.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FriendRequest.objects.count(), 0)

    def test_cannot_send_when_already_friends(self):
        Friendship.objects.create(user=self.alice, friend=self.bob)
        Friendship.objects.create(user=self.bob, friend=self.alice)

        response = self.client.post(self.url, {"to_user_id": self.bob.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FriendRequest.objects.count(), 0)

    def test_cannot_send_duplicate_pending(self):
        self.client.post(self.url, {"to_user_id": self.bob.id}, format="json")  # 201
        response = self.client.post(self.url, {"to_user_id": self.bob.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FriendRequest.objects.count(), 1)

    def test_cannot_send_when_reciprocal_pending(self):
        # Bob has already requested Alice — Alice should accept it, not duplicate.
        FriendRequest.objects.create(from_user=self.bob, to_user=self.alice)

        response = self.client.post(self.url, {"to_user_id": self.bob.id}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(FriendRequest.objects.count(), 1)

    def test_send_to_unknown_user_404(self):
        response = self.client.post(self.url, {"to_user_id": 999_999}, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ---------------------------------------------------------------------------
# Responding (accept / decline) and cancelling
# ---------------------------------------------------------------------------

class RespondFriendRequestTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user(
            username="alice", email="alice@example.com", password=PASSWORD
        )
        cls.bob = User.objects.create_user(
            username="bob", email="bob@example.com", password=PASSWORD
        )
        cls.carol = User.objects.create_user(
            username="carol", email="carol@example.com", password=PASSWORD
        )

    def _open_request(self, sender, recipient):
        return FriendRequest.objects.create(from_user=sender, to_user=recipient)

    # ----- accept ---------------------------------------------------------

    def test_accept_creates_friendship_and_deletes_request(self):
        fr = self._open_request(self.alice, self.bob)
        _login(self.client, self.bob)

        url = reverse("friend-request-detail", kwargs={"request_id": fr.id})
        response = self.client.patch(url, {"action": "accept"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(FriendRequest.objects.filter(id=fr.id).exists())
        # Two-row friendship: A→B and B→A.
        self.assertEqual(Friendship.objects.count(), 2)
        self.assertTrue(Friendship.objects.filter(user=self.alice, friend=self.bob).exists())
        self.assertTrue(Friendship.objects.filter(user=self.bob, friend=self.alice).exists())

    def test_non_recipient_cannot_accept(self):
        fr = self._open_request(self.alice, self.bob)
        _login(self.client, self.carol)

        url = reverse("friend-request-detail", kwargs={"request_id": fr.id})
        response = self.client.patch(url, {"action": "accept"}, format="json")

        # 400 by design — service treats "not found" and "not yours" the
        # same to avoid leaking the existence of other users' requests.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(FriendRequest.objects.filter(id=fr.id).exists())
        self.assertEqual(Friendship.objects.count(), 0)

    # ----- decline --------------------------------------------------------

    def test_decline_deletes_request_without_creating_friendship(self):
        fr = self._open_request(self.alice, self.bob)
        _login(self.client, self.bob)

        url = reverse("friend-request-detail", kwargs={"request_id": fr.id})
        response = self.client.patch(url, {"action": "decline"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FriendRequest.objects.filter(id=fr.id).exists())
        self.assertEqual(Friendship.objects.count(), 0)

    def test_can_resend_after_decline(self):
        # REGRESSION TEST.
        # Under the old `status='declined'` scheme the unique constraint
        # blocked re-requesting. Under delete-on-resolve this just works.
        fr = self._open_request(self.alice, self.bob)

        _login(self.client, self.bob)
        self.client.patch(
            reverse("friend-request-detail", kwargs={"request_id": fr.id}),
            {"action": "decline"},
            format="json",
        )

        self.client.logout()
        _login(self.client, self.alice)
        response = self.client.post(
            reverse("friend-request-collection"),
            {"to_user_id": self.bob.id},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # ----- invalid action -------------------------------------------------

    def test_invalid_action_returns_400(self):
        fr = self._open_request(self.alice, self.bob)
        _login(self.client, self.bob)

        url = reverse("friend-request-detail", kwargs={"request_id": fr.id})
        response = self.client.patch(url, {"action": "explode"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(FriendRequest.objects.filter(id=fr.id).exists())

    # ----- cancel ---------------------------------------------------------

    def test_cancel_by_sender_deletes_request(self):
        fr = self._open_request(self.alice, self.bob)
        _login(self.client, self.alice)

        url = reverse("friend-request-detail", kwargs={"request_id": fr.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(FriendRequest.objects.filter(id=fr.id).exists())

    def test_non_sender_cannot_cancel(self):
        fr = self._open_request(self.alice, self.bob)
        _login(self.client, self.bob)  # Bob is the recipient, not sender

        url = reverse("friend-request-detail", kwargs={"request_id": fr.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(FriendRequest.objects.filter(id=fr.id).exists())


# ---------------------------------------------------------------------------
# Friend list + remove
# ---------------------------------------------------------------------------

class FriendListAndRemoveTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user(
            username="alice", email="alice@example.com", password=PASSWORD
        )
        cls.bob = User.objects.create_user(
            username="bob", email="bob@example.com", password=PASSWORD
        )
        cls.carol = User.objects.create_user(
            username="carol", email="carol@example.com", password=PASSWORD
        )

        # Alice ↔ Bob (two rows).
        Friendship.objects.create(user=cls.alice, friend=cls.bob)
        Friendship.objects.create(user=cls.bob, friend=cls.alice)

    def test_friend_list_returns_other_user(self):
        _login(self.client, self.alice)
        response = self.client.get(reverse("friend-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["friend"]["username"], "bob")

        # Mirror check: Bob sees Alice.
        self.client.logout()
        _login(self.client, self.bob)
        body = self.client.get(reverse("friend-list")).json()
        self.assertEqual(body[0]["friend"]["username"], "alice")

    def test_remove_deletes_both_rows(self):
        _login(self.client, self.alice)
        url = reverse("friend-detail", kwargs={"user_id": self.bob.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Friendship.objects.count(), 0)

    def test_remove_non_friend_returns_400(self):
        _login(self.client, self.alice)
        url = reverse("friend-detail", kwargs={"user_id": self.carol.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# Relationship status
# ---------------------------------------------------------------------------

class RelationshipStatusTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user(
            username="alice", email="alice@example.com", password=PASSWORD
        )
        cls.bob = User.objects.create_user(
            username="bob", email="bob@example.com", password=PASSWORD
        )

    def _status(self, other) -> str:
        url = reverse("relationship-status", kwargs={"user_id": other.id})
        return self.client.get(url).json()["status"]

    def test_status_none(self):
        _login(self.client, self.alice)
        self.assertEqual(self._status(self.bob), "none")

    def test_status_request_sent_and_received(self):
        FriendRequest.objects.create(from_user=self.alice, to_user=self.bob)

        _login(self.client, self.alice)
        self.assertEqual(self._status(self.bob), "request_sent")

        self.client.logout()
        _login(self.client, self.bob)
        self.assertEqual(self._status(self.alice), "request_received")

    def test_status_friends(self):
        Friendship.objects.create(user=self.alice, friend=self.bob)
        Friendship.objects.create(user=self.bob, friend=self.alice)

        _login(self.client, self.alice)
        self.assertEqual(self._status(self.bob), "friends")


# ---------------------------------------------------------------------------
# Friend search
# ---------------------------------------------------------------------------

class FriendSearchTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.alice = User.objects.create_user(
            username="alice", email="alice@example.com", password=PASSWORD
        )
        cls.alfred = User.objects.create_user(
            username="alfred", email="alfred@example.com", password=PASSWORD
        )
        cls.bob = User.objects.create_user(
            username="bob", email="bob@example.com", password=PASSWORD
        )
        # Soft-deleted user must not appear in results.
        cls.inactive = User.objects.create_user(
            username="alzheimer", email="x@example.com",
            password=PASSWORD, is_active=False,
        )

    def setUp(self):
        _login(self.client, self.alice)
        self.url = reverse("friend-search")

    def test_returns_prefix_matches_excluding_self_and_inactive(self):
        response = self.client.get(self.url, {"q": "al"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        usernames = [row["username"] for row in response.json()]
        # alice (self) and alzheimer (inactive) must not appear.
        self.assertEqual(usernames, ["alfred"])

    def test_rejects_short_query(self):
        response = self.client.get(self.url, {"q": "a"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_no_match_returns_empty_list(self):
        response = self.client.get(self.url, {"q": "zzz"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_response_does_not_leak_email(self):
        response = self.client.get(self.url, {"q": "bo"})
        body = response.json()
        self.assertEqual(len(body), 1)
        # PublicUserSerializer must not include email.
        self.assertNotIn("email", body[0])