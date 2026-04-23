from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from game.models import GameSession, SessionPlayer, Question, SessionQuestion, AnswerAttempt
from game.services import start_answering_turn, submit_player_answer, evaluate_player_answer


"""
These tests cover service-layer orchestration and persistence.
They do NOT test raw FSM transitions in isolation.
"""


class ServicesTestCase(TestCase):
    def setUp(self):
        self.session = GameSession.objects.create(
            answer_time_limit_ms=20_000,
            current_status=GameSession.Status.ANSWERING,
        )

        self.p1 = SessionPlayer.objects.create(
            session=self.session,
            display_name="P1",
            seat_number=1,
        )
        self.p2 = SessionPlayer.objects.create(
            session=self.session,
            display_name="P2",
            seat_number=2,
        )

        q1 = Question.objects.create(question_text="Q1", correct_answer="A")
        q2 = Question.objects.create(question_text="Q2", correct_answer="B")

        self.sq1 = SessionQuestion.objects.create(session=self.session, question=q1, order_index=0)
        self.sq2 = SessionQuestion.objects.create(session=self.session, question=q2, order_index=1)

        self.session.current_player = self.p1
        self.session.current_question = self.sq1
        self.session.question_asked_count = 1
        self.session.save()
        self.session.refresh_from_db()

    def test_start_answering_turn_creates_pending_attempt_and_sets_current_attempt(self):
        start_answering_turn(self.session)
        self.session.refresh_from_db()

        attempt = self.session.current_attempt

        self.assertIsNotNone(attempt)
        self.assertEqual(attempt.session, self.session)
        self.assertEqual(attempt.player, self.p1)
        self.assertEqual(attempt.session_question, self.sq1)
        self.assertEqual(attempt.evaluation_status, AnswerAttempt.EvaluationStatus.PENDING)
        self.assertIsNone(attempt.is_correct)
        self.assertEqual(attempt.answer_time_ms, 0)
        self.assertIsNotNone(attempt.started_at)

    def test_start_answering_turn_requires_current_player(self):
        self.session.current_player = None
        self.session.save()

        with self.assertRaises(ValueError):
            start_answering_turn(self.session)

    def test_start_answering_turn_requires_current_question(self):
        self.session.current_question = None
        self.session.save()

        with self.assertRaises(ValueError):
            start_answering_turn(self.session)

    def test_start_answering_turn_requires_no_current_attempt(self):
        start_answering_turn(self.session)

        with self.assertRaises(ValueError):
            start_answering_turn(self.session)

    def test_submit_player_answer_fills_existing_attempt_and_moves_to_evaluation(self):
        start_answering_turn(self.session)
        self.session.refresh_from_db()

        attempt = self.session.current_attempt
        attempt.started_at = timezone.now() - timedelta(seconds=2)
        attempt.save()

        submit_player_answer(self.session, answer="A")
        self.session.refresh_from_db()
        attempt.refresh_from_db()

        self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)
        self.assertEqual(attempt.answer_text, "A")
        self.assertFalse(attempt.is_timeout)
        self.assertGreaterEqual(attempt.answer_time_ms, 2000)

    def test_submit_player_answer_marks_timeout_when_limit_is_exceeded(self):
        start_answering_turn(self.session)
        self.session.refresh_from_db()

        attempt = self.session.current_attempt
        attempt.started_at = timezone.now() - timedelta(seconds=30)
        attempt.save()

        submit_player_answer(self.session, answer="A")
        self.session.refresh_from_db()
        attempt.refresh_from_db()

        self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)
        self.assertTrue(attempt.is_timeout)
        self.assertIsNone(attempt.answer_text)
        self.assertGreaterEqual(attempt.answer_time_ms, self.session.answer_time_limit_ms)

    def test_submit_player_answer_requires_current_attempt(self):
        with self.assertRaises(ValueError):
            submit_player_answer(self.session, answer="A")

    def test_submit_player_answer_requires_current_player(self):
        start_answering_turn(self.session)
        self.session.current_player = None
        self.session.save()

        with self.assertRaises(ValueError):
            submit_player_answer(self.session, answer="A")

    def test_submit_player_answer_requires_current_question(self):
        start_answering_turn(self.session)
        self.session.current_question = None
        self.session.save()

        with self.assertRaises(ValueError):
            submit_player_answer(self.session, answer="A")

    def test_submit_player_answer_requires_pending_attempt(self):
        start_answering_turn(self.session)
        self.session.refresh_from_db()

        attempt = self.session.current_attempt
        attempt.evaluation_status = AnswerAttempt.EvaluationStatus.EVALUATED
        attempt.save()

        with self.assertRaises(ValueError):
            submit_player_answer(self.session, answer="A")

    def test_submit_player_answer_requires_started_at(self):
        start_answering_turn(self.session)
        self.session.refresh_from_db()

        attempt = self.session.current_attempt
        attempt.started_at = None
        attempt.save()

        with self.assertRaises(ValueError):
            submit_player_answer(self.session, answer="A")

    def test_evaluate_player_answer_marks_correct_attempt_and_enters_nomination(self):
        start_answering_turn(self.session)
        self.session.refresh_from_db()

        attempt = self.session.current_attempt
        attempt.started_at = timezone.now() - timedelta(seconds=1)
        attempt.save()

        submit_player_answer(self.session, answer="A")
        evaluate_player_answer(self.session)

        self.session.refresh_from_db()
        self.p1.refresh_from_db()
        attempt.refresh_from_db()

        self.assertEqual(attempt.evaluation_status, AnswerAttempt.EvaluationStatus.EVALUATED)
        self.assertTrue(attempt.is_correct)
        self.assertIsNotNone(attempt.evaluated_at)

        self.assertEqual(self.p1.points, 10)
        self.assertEqual(self.p1.answered_count, 1)
        self.assertEqual(self.session.last_correct_player, self.p1)
        self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)
        self.assertIsNone(self.session.current_attempt)

    def test_evaluate_player_answer_marks_wrong_attempt_and_falls_back_to_next_player(self):
        start_answering_turn(self.session)
        self.session.refresh_from_db()

        attempt = self.session.current_attempt
        attempt.started_at = timezone.now() - timedelta(seconds=1)
        attempt.save()

        submit_player_answer(self.session, answer="wrong")
        evaluate_player_answer(self.session)

        self.session.refresh_from_db()
        self.p1.refresh_from_db()
        attempt.refresh_from_db()

        self.assertEqual(attempt.evaluation_status, AnswerAttempt.EvaluationStatus.EVALUATED)
        self.assertFalse(attempt.is_correct)
        self.assertIsNotNone(attempt.evaluated_at)

        self.assertEqual(self.p1.lives, 2)
        self.assertEqual(self.p1.answered_count, 1)
        self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
        self.assertEqual(self.session.current_player, self.p2)
        self.assertEqual(self.session.current_question, self.sq2)
        self.assertIsNone(self.session.current_attempt)

    def test_evaluate_player_answer_treats_timeout_as_wrong(self):
        start_answering_turn(self.session)
        self.session.refresh_from_db()

        attempt = self.session.current_attempt
        attempt.started_at = timezone.now() - timedelta(seconds=30)
        attempt.save()

        submit_player_answer(self.session, answer="A")
        evaluate_player_answer(self.session)

        self.session.refresh_from_db()
        self.p1.refresh_from_db()
        attempt.refresh_from_db()

        self.assertTrue(attempt.is_timeout)
        self.assertFalse(attempt.is_correct)
        self.assertEqual(self.p1.lives, 2)
        self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)

    def test_evaluate_player_answer_requires_current_attempt(self):
        with self.assertRaises(ValueError):
            evaluate_player_answer(self.session)