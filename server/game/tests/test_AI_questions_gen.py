import uuid
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.test import SimpleTestCase, TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from game.models import GameSession, Question, SessionPlayer, SessionQuestion
from game.selectors.game_flow_selectors import get_game_snapshot
from game.serializers import GenerateExtraQuestionsResponseSerializer
from game.services.lobby.lobby_management import create_room
from game.services.question_generation.extra_question_generator import (
    GeneratedQuestion,
    generate,
    generate_extra_questions,
    persist_generated_questions,
)

User = get_user_model()


def _client_returning(parsed):
    """Build a fake genai client whose generate_content returns ``parsed``."""
    client = MagicMock()
    client.models.generate_content.return_value = MagicMock(parsed=parsed)
    return client


class GenerateParsingTest(SimpleTestCase):
    """Unit tests for the low-level ``generate`` LLM wrapper."""

    def test_returns_empty_list_when_parsed_is_none(self):
        client = _client_returning(None)
        self.assertEqual(generate(client, "model", "prompt"), [])

    def test_returns_empty_list_when_parsed_is_empty(self):
        client = _client_returning([])
        self.assertEqual(generate(client, "model", "prompt"), [])

    def test_passes_through_parsed_questions(self):
        parsed = [GeneratedQuestion(question="Q?", answers=["A"], category="c")]
        client = _client_returning(parsed)
        self.assertEqual(generate(client, "model", "prompt"), parsed)


class PersistGeneratedQuestionsGuardTest(TestCase):
    """``persist_generated_questions`` must tolerate empty/None input."""

    def setUp(self):
        self.session = GameSession.objects.create(current_status=GameSession.Status.LOBBY)

    def test_none_input_returns_empty_without_touching_db(self):
        self.assertEqual(persist_generated_questions(self.session, None), [])
        self.assertEqual(self.session.session_questions.count(), 0)
        self.assertEqual(Question.objects.filter(is_ai_generated=True).count(), 0)

    def test_empty_input_returns_empty(self):
        self.assertEqual(persist_generated_questions(self.session, []), [])
        self.assertEqual(self.session.session_questions.count(), 0)

    def test_persists_all_answer_variants_pipe_joined(self):
        generated = [
            GeneratedQuestion(
                question="Who formulated the three laws of motion?",
                answers=[" Isaac Newton ", "Newton", "Newton", "Sir Isaac Newton"],
                category="science",
            )
        ]
        ids = persist_generated_questions(self.session, generated)

        self.assertEqual(len(ids), 1)
        question = Question.objects.get(id=ids[0])
        # All variants kept (trimmed + deduplicated), joined with '|'.
        self.assertEqual(question.correct_answer, "Isaac Newton | Newton | Sir Isaac Newton")


class GenerateExtraQuestionsUnparseableTest(TestCase):
    """An unparseable LLM response must yield an empty result, not a crash."""

    def setUp(self):
        self.session = GameSession.objects.create(current_status=GameSession.Status.LOBBY)
        for i in range(4):
            question = Question.objects.create(
                question_text=f"Seed {i}?",
                correct_answer="A",
                category="general",
            )
            SessionQuestion.objects.create(session=self.session, question=question, order_index=i)

    @patch("game.services.question_generation.extra_question_generator.genai")
    @patch("game.services.question_generation.extra_question_generator.generate")
    def test_unparseable_response_yields_empty_result(self, mock_generate, mock_genai):
        # Simulate the LLM returning output that did not match the schema.
        mock_generate.return_value = None

        result = generate_extra_questions(self.session.session_uuid, 2)

        self.assertEqual(result, {"created_question_ids": []})
        self.assertEqual(self.session.session_questions.filter(question__is_ai_generated=True).count(), 0)


class GenerateExtraQuestionsApiTest(APITestCase):
    """API-level behaviour for POST /game/generate_extra_questions/."""

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

    def _make_host_session(self, real=0):
        """Create another LOBBY session hosted by self.host, with ``real`` questions."""
        session = GameSession.objects.create(current_status=GameSession.Status.LOBBY)
        host_sp = SessionPlayer.objects.create(
            session=session, user=self.host, display_name="Host", seat_number=1,
        )
        session.host_player = host_sp
        session.save()
        self._add_questions(real=real, session=session)
        return session

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
    def test_rejects_non_host(self, mock_generate):
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

    def test_missing_room_returns_404(self):
        url = reverse("generate-extra-questions")
        self.client.force_authenticate(user=self.host)
        response = self.client.post(
            url,
            {"session_uuid": str(uuid.uuid4())},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("game.services.lobby.lobby_management.generate_extra_questions")
    def test_rejects_started_room(self, mock_generate):
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
    def test_generation_allowed_once_per_session(self, mock_generate):
        mock_generate.return_value = {"created_question_ids": [1]}
        self._add_questions(real=10)

        url = reverse("generate-extra-questions")
        self.client.force_authenticate(user=self.host)
        payload = {"session_uuid": str(self.session.session_uuid)}

        first = self.client.post(url, payload, format="json")
        second = self.client.post(url, payload, format="json")

        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)
        self.session.refresh_from_db()
        self.assertTrue(self.session.extra_questions_generated)
        self.assertEqual(mock_generate.call_count, 1)

    def test_snapshot_exposes_extra_questions_generated_flag(self):
        snapshot = get_game_snapshot(self.session.id)
        self.assertIn("extra_questions_generated", snapshot)
        self.assertFalse(snapshot["extra_questions_generated"])

    @patch("game.services.lobby.lobby_management.generate_extra_questions")
    def test_is_limited_per_user_per_hour(self, mock_generate):
        mock_generate.return_value = {"created_question_ids": [1]}

        url = reverse("generate-extra-questions")
        self.client.force_authenticate(user=self.host)

        # Generation is once-per-session, so each request uses a fresh session.
        # The per-user hourly quota (5) blocks the 6th regardless of session.
        sessions = [self._make_host_session(real=10) for _ in range(6)]
        responses = [
            self.client.post(url, {"session_uuid": str(s.session_uuid)}, format="json")
            for s in sessions[:5]
        ]
        blocked = self.client.post(
            url, {"session_uuid": str(sessions[5].session_uuid)}, format="json",
        )

        self.assertTrue(all(response.status_code == status.HTTP_200_OK for response in responses))
        self.assertEqual(blocked.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(mock_generate.call_count, 5)

    @patch("game.services.lobby.lobby_management.generate_extra_questions")
    def test_response_matches_output_serializer(self, mock_generate):
        mock_generate.return_value = {"created_question_ids": [1, 2, 3]}
        self._add_questions(real=10)

        url = reverse("generate-extra-questions")
        self.client.force_authenticate(user=self.host)

        response = self.client.post(
            url,
            {"session_uuid": str(self.session.session_uuid)},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = GenerateExtraQuestionsResponseSerializer(data=response.data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        mock_generate.assert_called_once_with(self.session.session_uuid, 5)


class GenerateExtraQuestionsIntegrationTest(TestCase):
    """End-to-end: real service + persistence, only the LLM call mocked."""

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username="host", password="pass")
        self.client.force_login(self.user)

        # create verified questions FIRST (required by create_room)
        for i in range(10):
            Question.objects.create(
                question_text=f"Seed question {i}?",
                correct_answer=f"A{i}",
                category="general",
                is_verified=True,
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
        self.assertSetEqual(created_texts, {"AI Q1?", "AI Q2?", "AI Q3?"})

        # Check session was updated with new SessionQuestion entries
        after_session_q_count = self.session.session_questions.count()
        self.assertEqual(after_session_q_count, before_session_q_count + 3)

        attached_ai_questions = list(
            self.session.session_questions
            .filter(question__is_ai_generated=True)
            .values_list("question__question_text", flat=True)
        )

        self.assertSetEqual(set(attached_ai_questions), {"AI Q1?", "AI Q2?", "AI Q3?"})
        self.assertEqual(len(attached_ai_questions), 3)


class NewSessionUsesOnlyVerifiedQuestionsTest(TestCase):
    """A new room is seeded only with verified questions, which MAY be
    AI-generated. Unverified questions are never assigned."""

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username="host", password="pass")

    def test_only_verified_questions_are_assigned(self):
        for i in range(7):
            Question.objects.create(
                question_text=f"Verified real {i}?", correct_answer="A", category="general",
                is_verified=True,
            )
        for i in range(3):
            Question.objects.create(
                question_text=f"Verified AI {i}?", correct_answer="A", category="general",
                is_ai_generated=True, is_verified=True,
            )
        for i in range(20):
            Question.objects.create(
                question_text=f"Unverified AI {i}?", correct_answer="A", category="general",
                is_ai_generated=True, is_verified=False,
            )

        session = create_room(user=self.user)
        assigned = list(session.session_questions.select_related("question"))

        self.assertEqual(len(assigned), 10)
        # Everything assigned is verified...
        self.assertTrue(all(sq.question.is_verified for sq in assigned))
        # ...and verified AI questions are allowed (not excluded from the pool).
        self.assertEqual(sum(1 for sq in assigned if sq.question.is_ai_generated), 3)

    def test_unverified_questions_cannot_seed_a_room(self):
        for i in range(10):
            Question.objects.create(
                question_text=f"Unverified {i}?", correct_answer="A", category="general",
                is_verified=False,
            )
        with self.assertRaises(ValidationError):
            create_room(user=self.user)
