"""
Negative-path tests for the IsSelfOrReadOnly permission.

These tests must fail against the pre-fix code (where account/ endpoints
only required IsAuthenticated) and pass once IsSelfOrReadOnly is wired up
to UserDetailApi.patch and UserProfileAvatarApi.

The friend-permission cases lived against a UserProfile.friends M2M that
was removed (the relationship now lives in social.Friendship). Coverage
for friend boundaries lives in social/tests/test_friends.py.
"""

from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import User


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
        self.user_b.profile.avatar.save(
            "existing.png",
            SimpleUploadedFile("existing.png", _png_bytes(), content_type="image/png"),
            save=True,
        )
        self.user_b.profile.refresh_from_db()
        original_avatar_name = self.user_b.profile.avatar.name

        url = reverse("profile-avatar", kwargs={"user_id": self.user_b.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.user_b.profile.refresh_from_db()
        self.assertTrue(self.user_b.profile.avatar)
        self.assertEqual(self.user_b.profile.avatar.name, original_avatar_name)

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
