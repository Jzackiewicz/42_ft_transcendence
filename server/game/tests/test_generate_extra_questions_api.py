from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from game.models import GameSession, SessionPlayer

User = get_user_model()


class TestGenerateExtraQuestionsApi(APITestCase):
	def setUp(self):
		self.host = User.objects.create_user(username="host", email="host@test.com", password="password")
		self.player = User.objects.create_user(username="player", email="player@test.com", password="password")
		self.session = GameSession.objects.create(current_status=GameSession.Status.LOBBY)

		host_sp = SessionPlayer.objects.create(
			session=self.session,
			user=self.host,
			display_name="Host",
			seat_number=1,
		)
		self.session.host_player = host_sp
		self.session.save()

	@patch("game.apis.generate_extra_questions_for_room")
	def test_generate_extra_questions_success(self, mock_generate):
		mock_generate.return_value = {"created_question_ids": [123]}

		url = reverse("generate-extra-questions")
		self.client.force_authenticate(user=self.host)
		response = self.client.post(
			url,
			{"session_uuid": str(self.session.session_uuid), "n_questions_to_generate": 3},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data, mock_generate.return_value)
		# Print created IDs for visibility in test output
		print("Created question IDs:", response.data.get("created_question_ids"))
		mock_generate.assert_called_once_with(
			session_uuid=self.session.session_uuid,
			user=self.host,
			n_questions_to_generate=3,
		)

	@patch("game.apis.generate_extra_questions_for_room")
	def test_generate_extra_questions_uses_default_amount(self, mock_generate):
		mock_generate.return_value = {"created_question_ids": []}

		url = reverse("generate-extra-questions")
		self.client.force_authenticate(user=self.host)
		response = self.client.post(
			url,
			{"session_uuid": str(self.session.session_uuid)},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		mock_generate.assert_called_once_with(
			session_uuid=self.session.session_uuid,
			user=self.host,
			n_questions_to_generate=10,
		)

	@patch("game.apis.generate_extra_questions_for_room")
	def test_generate_extra_questions_rejects_non_host(self, mock_generate):
		url = reverse("generate-extra-questions")
		self.client.force_authenticate(user=self.player)
		response = self.client.post(
			url,
			{"session_uuid": str(self.session.session_uuid)},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("error", response.data)
		mock_generate.assert_not_called()

	def test_generate_extra_questions_missing_room_returns_404(self):
		url = reverse("generate-extra-questions")
		self.client.force_authenticate(user=self.host)
		response = self.client.post(
			url,
			{"session_uuid": str(uuid.uuid4())},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	@patch("game.apis.generate_extra_questions_for_room")
	def test_generate_extra_questions_rejects_started_room(self, mock_generate):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.save()

		url = reverse("generate-extra-questions")
		self.client.force_authenticate(user=self.host)
		response = self.client.post(
			url,
			{"session_uuid": str(self.session.session_uuid)},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn("error", response.data)
		mock_generate.assert_not_called()