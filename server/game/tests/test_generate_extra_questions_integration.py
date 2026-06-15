from unittest.mock import patch

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from game.models import Question, SessionQuestion
from game.services.lobby.lobby_management import create_room
from game.services.question_generation.extra_question_generator import GeneratedQuestion

class ExtraQuestionsIntegrationTest(TestCase):
    def setUp(self):
        cache.clear()
        User = get_user_model()
        self.user = User.objects.create_user(username="host", password="pass")
        self.client.force_login(self.user)

        # create questions FIRST (required by create_room)
        for i in range(10):
            Question.objects.create(
                question_text=f"Seed question {i}?",
                correct_answer=f"A{i}",
                category="general",
            )

        # now create the lobby (it will pick from existing questions)
        self.session = create_room(user=self.user)

    @patch("game.services.question_generation.extra_question_generator.generate")
    def test_generate_extra_questions_api_creates_and_attaches(self, mock_generate):
        # Mock LLM response as a simple list of question dicts
        mock_generate.return_value = [
            GeneratedQuestion(question="AI Q1?", answers=["A1"], category="general"),
            GeneratedQuestion(question="AI Q2?", answers=["A2"], category="general"),
            GeneratedQuestion(question="AI Q3?", answers=["A3"], category="general"),
        ]

        url = reverse("generate-extra-questions")
        payload = {
            "session_uuid": str(self.session.session_uuid),
            "n_questions_to_generate": 3,
        }

        before_q_count = Question.objects.filter(is_ai_generated=True).count()
        before_session_q_count = self.session.session_questions.count()

        resp = self.client.post(url, payload, content_type="application/json")
        self.assertEqual(resp.status_code, 200)

        body = resp.json()
        self.assertIn("created_question_ids", body)
        self.assertEqual(len(body["created_question_ids"]), 3)

        # Refresh session from DB
        self.session.refresh_from_db()

        # Check DB: AI-generated questions were created
        after_q_count = Question.objects.filter(is_ai_generated=True).count()
        self.assertEqual(after_q_count, before_q_count + 3)

        created_ids = body["created_question_ids"]
        created_texts = set(
            Question.objects.filter(id__in=created_ids)
            .values_list("question_text", flat=True)
        )
        self.assertSetEqual(
            created_texts,
            {"AI Q1?", "AI Q2?", "AI Q3?"}
        )

        # Check session was updated with new SessionQuestion entries
        after_session_q_count = self.session.session_questions.count()
        self.assertEqual(after_session_q_count, before_session_q_count + 3)

        attached_ai_questions = list(
            self.session.session_questions
            .filter(question__is_ai_generated=True)
            .values_list("question__question_text", flat=True)
        )

        self.assertSetEqual(
            set(attached_ai_questions),
            {"AI Q1?", "AI Q2?", "AI Q3?"}
        )

        self.assertEqual(len(attached_ai_questions), 3)