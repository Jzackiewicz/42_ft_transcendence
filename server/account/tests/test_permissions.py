"""
Negative-path tests for the IsSelfOrReadOnly permission.

These tests must fail against the pre-fix code (where account/ endpoints
only required IsAuthenticated) and pass once IsSelfOrReadOnly is wired up
to UserDetailApi.patch, UserProfileAvatarApi, and UserProfileFriendDetailApi.

User A is the actor in every negative case; users B and C are passive
targets. We assert both the HTTP status and the underlying DB state — a
buggy implementation that returned 403 but still mutated would slip past
a status-only check.
"""

from io import BytesIO

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


def _png_bytes() -> bytes:
    """Smallest valid PNG payload — needed because ImageField actually
    decodes the upload, so we can't get away with `b'not-an-image'`."""
    buf = BytesIO()
    Image.new("RGB", (1, 1), color="red").save(buf, format="PNG")
    return buf.getvalue()


class IsSelfOrReadOnlyTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_a = User.objects.create_user(
            username="alice", email="alice@example.com", password="pw-aaaa-1234"
        )
        cls.user_b = User.objects.create_user(
            username="bob", email="bob@example.com", password="pw-bbbb-1234"
        )
        cls.user_c = User.objects.create_user(
            username="carol", email="carol@example.com", password="pw-cccc-1234"
        )

    def setUp(self):
        # Log in as A for every negative-path test. Positive-path tests
        # that need a different actor re-login explicitly.
        self.client.login(username="alice", password="pw-aaaa-1234")

    # -------------------- UserDetailApi.patch --------------------

    def test_user_a_cannot_patch_user_b(self):
        url = reverse("user-detail", kwargs={"user_id": self.user_b.id})
        response = self.client.patch(url, {"username": "hacked"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.user_b.refresh_from_db()
        self.assertEqual(self.user_b.username, "bob")

    def test_user_a_can_patch_self(self):
        url = reverse("user-detail", kwargs={"user_id": self.user_a.id})
        response = self.client.patch(url, {"username": "alice2"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_a.refresh_from_db()
        self.assertEqual(self.user_a.username, "alice2")

    def test_user_detail_get_remains_open_to_authenticated(self):
        # Guards the documented policy: GET stays open even on someone
        # else's record. If this ever flips to 403, the policy comment
        # in apis.py should be updated too.
        url = reverse("user-detail", kwargs={"user_id": self.user_b.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -------------------- UserProfileAvatarApi --------------------

    def test_user_a_cannot_upload_avatar_to_user_b(self):
        url = reverse("profile-avatar", kwargs={"user_id": self.user_b.id})
        avatar = SimpleUploadedFile("a.png", _png_bytes(), content_type="image/png")
        response = self.client.post(url, {"avatar": avatar}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.user_b.profile.refresh_from_db()
        self.assertFalse(self.user_b.profile.avatar)

    def test_user_a_cannot_delete_user_b_avatar(self):
        url = reverse("profile-avatar", kwargs={"user_id": self.user_b.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # -------------------- UserProfileFriendDetailApi --------------------

    def test_user_a_cannot_add_friend_to_user_b(self):
        url = reverse(
            "profile-friend-detail",
            kwargs={"user_id": self.user_b.id, "friend_user_id": self.user_c.id},
        )
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            self.user_b.profile.friends.filter(pk=self.user_c.profile.pk).exists()
        )

    def test_user_a_cannot_remove_friend_from_user_b(self):
        # Pre-seed B↔C at the model level so this would actually mutate
        # state if the permission were missing — a 403 alone wouldn't
        # prove the request was rejected before reaching the service.
        self.user_b.profile.friends.add(self.user_c.profile)

        url = reverse(
            "profile-friend-detail",
            kwargs={"user_id": self.user_b.id, "friend_user_id": self.user_c.id},
        )
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(
            self.user_b.profile.friends.filter(pk=self.user_c.profile.pk).exists()
        )