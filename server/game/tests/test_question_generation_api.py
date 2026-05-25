from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase


User = get_user_model()


class QuestionGenerationApiTests(APITestCase):
	def setUp(self) -> None:
		self.user = User.objects.create_user(
			username="generator",
			password="generator-password",
			email="generator@example.com",
		)

	def test_generate_questions_requires_authentication(self):
		response = self.client.post(
			reverse("question-generate"),
			{"category": "History", "question_count": 3},
			format="json",
		)

		self.assertEqual(response.status_code, 403)

	@patch("game.views.generate_questions")
	def test_generate_questions_returns_json_payload(self, mock_generate_questions):
		self.client.login(username="generator", password="generator-password")
		mock_generate_questions.return_value = {
			"requested_category": "History",
			"question_count": 2,
			"questions": [
				{
					"category": "Ancient History",
					"question": "Who was the first emperor of Rome?",
					"answer": ["Augustus", "Octavian"],
				},
				{
					"category": "Modern History",
					"question": "Which wall fell in 1989?",
					"answer": ["Berlin Wall"],
				},
			],
		}

		response = self.client.post(
			reverse("question-generate"),
			{"category": "History", "question_count": 2},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["requested_category"], "History")
		self.assertEqual(response.data["question_count"], 2)
		self.assertEqual(len(response.data["questions"]), 2)
		mock_generate_questions.assert_called_once_with(category="History", question_count=2)