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
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
import shutil
import tempfile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


def _png_bytes() -> bytes:
    """Smallest valid PNG payload — needed because ImageField actually
    decodes the upload, so we can't get away with `b'not-an-image'`."""
    buf = BytesIO()
    Image.new("RGB", (1, 1), color="red").save(buf, format="PNG")
    return buf.getvalue()


TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class IsSelfOrReadOnlyTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

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

    def test_upload_avatar_exceeding_size_limit_returns_400(self):
        url = reverse("profile-avatar", kwargs={"user_id": self.user_a.id})
        large_data = _png_bytes() + (b"0" * (5 * 1024 * 1024 + 1))
        avatar = SimpleUploadedFile("large.png", large_data, content_type="image/png")
        response = self.client.post(url, {"avatar": avatar}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("avatar", response.data)
        self.assertEqual(
            response.data["avatar"][0], "Avatar file size must be under 5MB."
        )

    def test_upload_avatar_within_size_limit_succeeds(self):
        url = reverse("profile-avatar", kwargs={"user_id": self.user_a.id})
        avatar = SimpleUploadedFile("valid.png", _png_bytes(), content_type="image/png")
        response = self.client.post(url, {"avatar": avatar}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user_a.profile.refresh_from_db()
        self.assertTrue(self.user_a.profile.avatar)
