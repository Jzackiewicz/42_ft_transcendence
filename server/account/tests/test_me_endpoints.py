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

    def test_profile_me_endpoint_patch_duplicate_username_different_case(self):
        User.objects.create_user(
            username="otheruser", password="otherpassword", email="other@example.com"
        )
        self.client.login(username="profileuser", password="profilepassword")
        payload = {"username": "OTHERUSER"}
        response = self.client.patch(
            reverse("profile-me"), data=payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)


    def test_profile_me_endpoint_patch_duplicate_email_different_case(self):
        User.objects.create_user(
            username="otheruser", password="otherpassword", email="other@example.com"
        )
        self.client.login(username="profileuser", password="profilepassword")
        payload = {"email": "OTHER@EXAMPLE.COM"}
        response = self.client.patch(
            reverse("profile-me"), data=payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)


    def test_profile_me_endpoint_patch_rejects_too_short_username(self):
        self.client.login(username="profileuser", password="profilepassword")
        payload = {"username": "ab"}
        response = self.client.patch(
            reverse("profile-me"), data=payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)

    def test_profile_me_endpoint_patch_rejects_overlong_email(self):
        # 255 chars total (244 local + "@example.com") exceeds the 254 limit and
        # must return a clean 400 rather than blowing up at the DB (500).
        long_email = "a" * 244 + "@example.com"
        self.assertGreater(len(long_email), 254)
        self.client.login(username="profileuser", password="profilepassword")
        response = self.client.patch(
            reverse("profile-me"),
            data={"email": long_email},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.data)

    def test_profile_me_endpoint_patch_rejects_at_sign_in_username(self):
        self.client.login(username="profileuser", password="profilepassword")
        payload = {"username": "alice@bar.com"}
        response = self.client.patch(
            reverse("profile-me"), data=payload, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)

    def test_other_users_emails_are_hidden_in_list_and_detail(self):
        other_user = User.objects.create_user(
            username="otheruser",
            password="otherpassword",
            email="other@example.com",
        )
        self.client.login(username="profileuser", password="profilepassword")

        # Test profile detail endpoint (other user)
        response = self.client.get(reverse("profile-detail", kwargs={"user_id": other_user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("email", response.data["user"])

        # Test profile detail endpoint (own user)
        response = self.client.get(reverse("profile-detail", kwargs={"user_id": self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["user"]["email"], "profile@example.com")

        # Test user detail endpoint (other user)
        response = self.client.get(reverse("user-detail", kwargs={"user_id": other_user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("email", response.data)

        # Test user detail endpoint (own user)
        response = self.client.get(reverse("user-detail", kwargs={"user_id": self.user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "profile@example.com")
