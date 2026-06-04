from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


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

    def test_profile_me_endpoint_get_unauthenticated(self):
        response = self.client.get(reverse("profile-me"))
        self.assertEqual(response.status_code, 401)

    def test_profile_me_endpoint_patch_success(self):
        self.client.login(username="profileuser", password="profilepassword")
        payload = {"username": "newprofileuser", "email": "newprofile@example.com"}
        response = self.client.patch(
            reverse("profile-me"), data=payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # Should return profile data
        self.assertEqual(response.data["user"]["username"], "newprofileuser")
        self.assertEqual(response.data["user"]["email"], "newprofile@example.com")

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "newprofileuser")
        self.assertEqual(self.user.email, "newprofile@example.com")

    def test_profile_me_endpoint_patch_unauthenticated(self):
        response = self.client.patch(reverse("profile-me"))
        self.assertEqual(response.status_code, 401)

    def test_profile_me_endpoint_patch_duplicate_username(self):
        User.objects.create_user(
            username="otheruser", password="otherpassword", email="other@example.com"
        )
        self.client.login(username="profileuser", password="profilepassword")
        payload = {"username": "otheruser"}
        response = self.client.patch(
            reverse("profile-me"), data=payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)

    def test_profile_me_endpoint_patch_duplicate_email(self):
        User.objects.create_user(
            username="otheruser", password="otherpassword", email="other@example.com"
        )
        self.client.login(username="profileuser", password="profilepassword")
        payload = {"email": "other@example.com"}
        response = self.client.patch(
            reverse("profile-me"), data=payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_profile_me_endpoint_delete_success(self):
        self.client.login(username="profileuser", password="profilepassword")
        payload = {"password": "profilepassword"}
        response = self.client.delete(
            reverse("profile-me"), data=payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 204)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_profile_me_endpoint_delete_invalid_password(self):
        self.client.login(username="profileuser", password="profilepassword")
        payload = {"password": "wrongpassword"}
        response = self.client.delete(
            reverse("profile-me"), data=payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 401)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_profile_me_endpoint_delete_unauthenticated(self):
        response = self.client.delete(reverse("profile-me"))
        self.assertEqual(response.status_code, 401)
