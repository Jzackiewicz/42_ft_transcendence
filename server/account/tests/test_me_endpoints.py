from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class MeTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", email="test@example.com"
        )

    def test_me_endpoint_get_success(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("user-me"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")

    def test_me_endpoint_get_unauthenticated(self):
        response = self.client.get(reverse("user-me"))
        self.assertEqual(response.status_code, 403)

    def test_me_endpoint_patch_success(self):
        self.client.login(username="testuser", password="testpassword")
        payload = {"username": "newusername", "email": "new@example.com"}
        response = self.client.patch(
            reverse("user-me"), data=payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "newusername")
        self.assertEqual(self.user.email, "new@example.com")

    def test_me_endpoint_patch_unauthenticated(self):
        response = self.client.patch(reverse("user-me"))
        self.assertEqual(response.status_code, 403)

    def test_me_endpoint_patch_duplicate_username(self):
        User.objects.create_user(
            username="otheruser", password="otherpassword", email="other@example.com"
        )
        self.client.login(username="testuser", password="testpassword")
        payload = {"username": "otheruser"}
        response = self.client.patch(
            reverse("user-me"), data=payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)

    def test_me_endpoint_patch_duplicate_email(self):
        User.objects.create_user(
            username="otheruser", password="otherpassword", email="other@example.com"
        )
        self.client.login(username="testuser", password="testpassword")
        payload = {"email": "other@example.com"}
        response = self.client.patch(
            reverse("user-me"), data=payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_me_endpoint_delete_success(self):
        self.client.login(username="testuser", password="testpassword")
        payload = {"password": "testpassword"}
        response = self.client.delete(
            reverse("user-me"), data=payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 204)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_me_endpoint_delete_invalid_password(self):
        self.client.login(username="testuser", password="testpassword")
        payload = {"password": "wrongpassword"}
        response = self.client.delete(
            reverse("user-me"), data=payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_me_endpoint_delete_unauthenticated(self):
        response = self.client.delete(reverse("user-me"))
        self.assertEqual(response.status_code, 403)


class UserProfileMeTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="profileuser",
            password="profilepassword",
            email="profile@example.com",
        )

    def test_profile_me_endpoint_success(self):
        self.client.login(username="profileuser", password="profilepassword")
        response = self.client.get(reverse("profile-me"))
        self.assertEqual(response.status_code, 200)

        # Check structure based on UserProfileOutputSerializer
        self.assertIn("id", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "profileuser")
        self.assertEqual(response.data["user"]["email"], "profile@example.com")
        self.assertIn("avatar", response.data)
        self.assertIn("is_online", response.data)

    def test_profile_me_endpoint_unauthenticated(self):
        response = self.client.get(reverse("profile-me"))
        self.assertEqual(response.status_code, 403)


class UserMeExportTest(APITestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser", password="testpassword", email="test@example.com"
        )

    def test_me_export_endpoint_get_success(self):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("user-me-export"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["email"], "test@example.com")

    def test_me_export_endpoint_get_unauthenticated(self):
        response = self.client.get(reverse("user-me-export"))
        self.assertEqual(response.status_code, 403)
