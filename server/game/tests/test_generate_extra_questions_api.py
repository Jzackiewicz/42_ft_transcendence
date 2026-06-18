from unittest.mock import patch
import uuid

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from game.models import GameSession, SessionPlayer, Question, SessionQuestion
from game.serializers import GameSessionOutputSerializer, SessionPlayerOutputSerializer, GenerateExtraQuestionsPayloadSerializer, GenerateExtraQuestionsResponseSerializer

User = get_user_model()


class TestGenerateExtraQuestionsApi(APITestCase):
	def setUp(self):
		cache.clear()
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

	def _add_questions(self, real=0, ai=0, session=None):
		"""Attach ``real`` non-AI and ``ai`` AI-generated questions to the session."""
		session = session or self.session
		start = session.session_questions.count()
		for i in range(real + ai):
			question = Question.objects.create(
				question_text=f"Q{start + i}-{uuid.uuid4()}?",
				correct_answer="A",
				category="general",
				is_ai_generated=(i >= real),
			)
			SessionQuestion.objects.create(
				session=session,
				question=question,
				order_index=start + i,
			)

	@patch("game.services.lobby.lobby_management.generate_extra_questions")
	def test_generates_half_of_real_questions(self, mock_generate):
		mock_generate.return_value = {"created_question_ids": [123]}
		self._add_questions(real=10)

		url = reverse("generate-extra-questions")
		self.client.force_authenticate(user=self.host)
		response = self.client.post(
			url,
			{"session_uuid": str(self.session.session_uuid)},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data, mock_generate.return_value)
		# 50% of 10 real questions = 5
		mock_generate.assert_called_once_with(self.session.session_uuid, 5)

	@patch("game.services.lobby.lobby_management.generate_extra_questions")
	def test_rounds_half_up(self, mock_generate):
		mock_generate.return_value = {"created_question_ids": []}
		self._add_questions(real=7)

		url = reverse("generate-extra-questions")
		self.client.force_authenticate(user=self.host)
		response = self.client.post(
			url,
			{"session_uuid": str(self.session.session_uuid)},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		# 50% of 7 = 3.5, rounded up = 4
		mock_generate.assert_called_once_with(self.session.session_uuid, 4)

	@patch("game.services.lobby.lobby_management.generate_extra_questions")
	def test_ai_questions_excluded_from_base(self, mock_generate):
		mock_generate.return_value = {"created_question_ids": []}
		self._add_questions(real=10, ai=8)

		url = reverse("generate-extra-questions")
		self.client.force_authenticate(user=self.host)
		response = self.client.post(
			url,
			{"session_uuid": str(self.session.session_uuid)},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		# Only the 10 real questions count toward the base: 50% = 5
		mock_generate.assert_called_once_with(self.session.session_uuid, 5)

	@patch("game.services.lobby.lobby_management.generate_extra_questions")
	def test_no_real_questions_skips_generation(self, mock_generate):
		url = reverse("generate-extra-questions")
		self.client.force_authenticate(user=self.host)
		response = self.client.post(
			url,
			{"session_uuid": str(self.session.session_uuid)},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data, {"created_question_ids": []})
		mock_generate.assert_not_called()

	@patch("game.services.lobby.lobby_management.generate_extra_questions")
	def test_rejects_unknown_payload_field(self, mock_generate):
		self._add_questions(real=10)

		url = reverse("generate-extra-questions")
		self.client.force_authenticate(user=self.host)
		response = self.client.post(
			url,
			{"session_uuid": str(self.session.session_uuid), "n_questions_to_generate": 3},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		mock_generate.assert_not_called()

	@patch("game.services.lobby.lobby_management.generate_extra_questions")
	def test_generate_extra_questions_rejects_non_host(self, mock_generate):
		self._add_questions(real=10)

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

	@patch("game.services.lobby.lobby_management.generate_extra_questions")
	def test_generate_extra_questions_rejects_started_room(self, mock_generate):
		self._add_questions(real=10)
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

	@patch("game.services.lobby.lobby_management.generate_extra_questions")
	def test_generate_extra_questions_is_limited_per_user_per_hour(self, mock_generate):
		mock_generate.return_value = {"created_question_ids": [1]}
		self._add_questions(real=10)

		url = reverse("generate-extra-questions")
		self.client.force_authenticate(user=self.host)

		responses = [
			self.client.post(
				url,
				{"session_uuid": str(self.session.session_uuid)},
				format="json",
			)
			for _ in range(5)
		]
		blocked = self.client.post(
			url,
			{"session_uuid": str(self.session.session_uuid)},
			format="json",
		)

		self.assertTrue(all(response.status_code == status.HTTP_200_OK for response in responses))
		self.assertEqual(blocked.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
		self.assertEqual(mock_generate.call_count, 5)

	@patch("game.services.lobby.lobby_management.generate_extra_questions")
	def test_response_matches_output_serializer(self, mock_generate):
		mock_generate.return_value = {
			"created_question_ids": [1, 2, 3]
		}
		self._add_questions(real=10)

		url = reverse("generate-extra-questions")
		self.client.force_authenticate(user=self.host)

		response = self.client.post(
			url,
			{"session_uuid": str(self.session.session_uuid)},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

		serializer = GenerateExtraQuestionsResponseSerializer(
			data=response.data
		)
		self.assertTrue(serializer.is_valid(), serializer.errors)

		mock_generate.assert_called_once_with(self.session.session_uuid, 5)
