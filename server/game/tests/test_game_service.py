# game/tests/test_game_service.py

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from game.models import (
    AnswerAttempt,
    GameSession,
    Question,
    SessionPlayer,
    SessionQuestion,
)
from game.services.game_service import GameService


class GameServiceTests(TestCase):
    def setUp(self):
        self.session = GameSession.objects.create(answer_time_limit_ms=20_000)

        self.p1 = SessionPlayer.objects.create(
            session=self.session,
            display_name="P1",
            seat_number=1,
            lives=3,
        )
        self.p2 = SessionPlayer.objects.create(
            session=self.session,
            display_name="P2",
            seat_number=2,
            lives=3,
        )
        self.p3 = SessionPlayer.objects.create(
            session=self.session,
            display_name="P3",
            seat_number=3,
            lives=3,
        )

        self.q1 = Question.objects.create(
            question_text="2 + 2?",
            correct_answer="4",
            category="math",
        )
        self.q2 = Question.objects.create(
            question_text="Capital of Poland?",
            correct_answer="Warsaw",
            category="geo",
        )
        self.q3 = Question.objects.create(
            question_text="Color of sky?",
            correct_answer="blue",
            category="general",
        )
        self.q4 = Question.objects.create(
            question_text="5 + 5?",
            correct_answer="10",
            category="math",
        )

        self.sq1 = SessionQuestion.objects.create(
            session=self.session,
            question=self.q1,
            order_index=0,
        )
        self.sq2 = SessionQuestion.objects.create(
            session=self.session,
            question=self.q2,
            order_index=1,
        )
        self.sq3 = SessionQuestion.objects.create(
            session=self.session,
            question=self.q3,
            order_index=2,
        )
        self.sq4 = SessionQuestion.objects.create(
            session=self.session,
            question=self.q4,
            order_index=3,
        )

    def refresh(self):
        self.session.refresh_from_db()
        self.p1.refresh_from_db()
        self.p2.refresh_from_db()
        self.p3.refresh_from_db()

    def test_start_game_moves_to_answering_and_creates_attempt(self):
        GameService(self.session).start_game_session()
        self.session.refresh_from_db()

        self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
        self.assertIsNotNone(self.session.started_at)
        self.assertIsNotNone(self.session.current_player)
        self.assertIsNotNone(self.session.current_question)
        self.assertIsNotNone(self.session.current_attempt)
        self.assertEqual(
            self.session.current_attempt.evaluation_status,
            AnswerAttempt.EvaluationStatus.PENDING,
        )
        self.assertEqual(self.session.question_asked_count, 1)

    def test_start_game_requires_lobby_state(self):
        self.session.current_status = GameSession.Status.ANSWERING
        self.session.save()

        with self.assertRaisesMessage(ValueError, "Game session is not in lobby state"):
            GameService(self.session).start_game_session()

    def test_start_game_requires_at_least_two_players(self):
        self.p2.delete()
        self.p3.delete()

        with self.assertRaisesMessage(
            ValueError,
            "Cannot start game with fewer than 2 players",
        ):
            GameService(self.session).start_game_session()

    def test_start_game_requires_questions(self):
        self.session.session_questions.all().delete()

        with self.assertRaisesMessage(
            ValueError,
            "Cannot start game without questions",
        ):
            GameService(self.session).start_game_session()

    def test_submit_answer_by_current_player_moves_to_evaluation(self):
        GameService(self.session).start_game_session()
        self.session.refresh_from_db()

        actor = self.session.current_player

        GameService(self.session).submit_player_answer(actor=actor, answer="4")
        self.session.refresh_from_db()

        attempt = self.session.current_attempt
        attempt.refresh_from_db()

        self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)
        self.assertEqual(attempt.answer_text, "4")
        self.assertFalse(attempt.is_timeout)
        self.assertGreaterEqual(attempt.answer_time_ms, 0)

    def test_submit_answer_rejects_non_current_player(self):
        GameService(self.session).start_game_session()
        self.session.refresh_from_db()

        actor = self.session.session_players.exclude(
            id=self.session.current_player_id
        ).first()

        with self.assertRaisesMessage(ValueError, "Only current player can submit answer"):
            GameService(self.session).submit_player_answer(actor=actor, answer="4")

    def test_submit_answer_timeout_ignores_answer_text(self):
        GameService(self.session).start_game_session()
        self.session.refresh_from_db()

        attempt = self.session.current_attempt
        attempt.started_at = timezone.now() - timedelta(seconds=30)
        attempt.save()

        actor = self.session.current_player

        GameService(self.session).submit_player_answer(actor=actor, answer="4")
        self.session.refresh_from_db()

        attempt.refresh_from_db()

        self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)
        self.assertTrue(attempt.is_timeout)
        self.assertIsNone(attempt.answer_text)

    def test_evaluate_correct_answer_adds_points_and_goes_to_nomination(self):
        GameService(self.session).start_game_session()
        self.session.refresh_from_db()

        actor = self.session.current_player
        correct_answer = self.session.current_question.question.correct_answer

        GameService(self.session).submit_player_answer(
            actor=actor,
            answer=correct_answer,
        )
        self.session.refresh_from_db()

        GameService(self.session).evaluate_player_answer()
        self.session.refresh_from_db()
        actor.refresh_from_db()

        self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)
        self.assertEqual(self.session.last_correct_player_id, actor.id)
        self.assertEqual(actor.points, 10)
        self.assertEqual(actor.answered_count, 1)
        self.assertIsNone(self.session.current_attempt)

    def test_evaluate_correct_answer_gives_20_points_if_player_was_nominated(self):
        self.session.current_status = GameSession.Status.ANSWERING
        self.session.current_player = self.p2
        self.session.last_nominated_player = self.p2
        self.session.save()

        GameService(self.session)._start_answering_turn()
        self.session.refresh_from_db()

        GameService(self.session).submit_player_answer(actor=self.p2, answer="4")
        self.session.refresh_from_db()

        GameService(self.session).evaluate_player_answer()
        self.p2.refresh_from_db()

        self.assertEqual(self.p2.points, 20)

    def test_wrong_answer_without_last_correct_player_fallbacks_to_next_alive_player_and_starts_new_attempt(self):
        self.session.current_status = GameSession.Status.ANSWERING
        self.session.current_player = self.p1
        self.session.save()

        GameService(self.session)._start_answering_turn()
        self.session.refresh_from_db()

        old_attempt_id = self.session.current_attempt_id

        GameService(self.session).submit_player_answer(actor=self.p1, answer="wrong")
        self.session.refresh_from_db()

        GameService(self.session).evaluate_player_answer()
        self.session.refresh_from_db()
        self.p1.refresh_from_db()

        self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
        self.assertEqual(self.session.current_player_id, self.p2.id)
        self.assertEqual(self.p1.lives, 2)
        self.assertIsNotNone(self.session.current_attempt)
        self.assertNotEqual(self.session.current_attempt_id, old_attempt_id)
        self.assertEqual(self.session.question_asked_count, 2)

    def test_wrong_answer_with_alive_last_correct_player_goes_to_nomination(self):
        self.session.current_status = GameSession.Status.ANSWERING
        self.session.current_player = self.p2
        self.session.last_correct_player = self.p1
        self.session.save()

        GameService(self.session)._start_answering_turn()
        self.session.refresh_from_db()

        GameService(self.session).submit_player_answer(actor=self.p2, answer="wrong")
        self.session.refresh_from_db()

        GameService(self.session).evaluate_player_answer()
        self.session.refresh_from_db()
        self.p2.refresh_from_db()

        self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)
        self.assertEqual(self.session.last_correct_player_id, self.p1.id)
        self.assertEqual(self.p2.lives, 2)
        self.assertIsNone(self.session.current_attempt)

    def test_nominate_player_sets_target_as_current_and_starts_new_attempt(self):
        self.session.current_status = GameSession.Status.NOMINATION
        self.session.last_correct_player = self.p1
        self.session.current_player = self.p1
        self.session.save()

        GameService(self.session).nominate_player(
            actor=self.p1,
            target_player_id=self.p3.id,
        )
        self.session.refresh_from_db()

        self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
        self.assertEqual(self.session.last_nominated_player_id, self.p3.id)
        self.assertEqual(self.session.current_player_id, self.p3.id)
        self.assertIsNotNone(self.session.current_attempt)

    def test_nominate_player_rejects_non_last_correct_player(self):
        self.session.current_status = GameSession.Status.NOMINATION
        self.session.last_correct_player = self.p1
        self.session.current_player = self.p1
        self.session.save()

        with self.assertRaisesMessage(ValueError, "Only last correct player can nominate"):
            GameService(self.session).nominate_player(
                actor=self.p2,
                target_player_id=self.p3.id,
            )

    def test_nominate_player_rejects_dead_target(self):
        self.session.current_status = GameSession.Status.NOMINATION
        self.session.last_correct_player = self.p1
        self.session.current_player = self.p1
        self.p3.lives = 0
        self.p3.save()
        self.session.save()

        with self.assertRaisesMessage(ValueError, "Cannot nominate a dead player"):
            GameService(self.session).nominate_player(
                actor=self.p1,
                target_player_id=self.p3.id,
            )

    def test_game_over_when_only_one_player_alive_sets_winner_and_end_reason(self):
        self.p2.lives = 0
        self.p2.save()
        self.p3.lives = 0
        self.p3.save()

        self.session.current_status = GameSession.Status.GAME_OVER
        self.session.current_player = self.p1
        self.session.current_question = self.sq1
        self.session.save()

        GameService(self.session).end_game_session()
        self.session.refresh_from_db()

        self.assertEqual(self.session.winner_id, self.p1.id)
        self.assertEqual(
            self.session.end_reason,
            GameSession.EndReason.LAST_PLAYER_ALIVE,
        )
        self.assertIsNotNone(self.session.ended_at)
        self.assertIsNone(self.session.current_question)
        self.assertIsNone(self.session.current_attempt)

    def test_game_over_by_questions_exhausted_uses_points_answered_count_time_and_seat_tiebreaker(self):
        self.p1.points = 20
        self.p1.answered_count = 2
        self.p1.total_answer_time_ms = 9000
        self.p1.save()

        self.p2.points = 20
        self.p2.answered_count = 2
        self.p2.total_answer_time_ms = 7000
        self.p2.save()

        self.p3.points = 10
        self.p3.answered_count = 3
        self.p3.total_answer_time_ms = 1000
        self.p3.save()

        self.session.current_status = GameSession.Status.GAME_OVER
        self.session.question_asked_count = self.session.session_questions.count()
        self.session.save()

        GameService(self.session).end_game_session()
        self.session.refresh_from_db()

        self.assertEqual(self.session.winner_id, self.p2.id)
        self.assertEqual(
            self.session.end_reason,
            GameSession.EndReason.QUESTIONS_EXHAUSTED,
        )

    def test_game_over_final_tiebreaker_uses_lower_seat_number(self):
        self.p1.points = 20
        self.p1.answered_count = 2
        self.p1.total_answer_time_ms = 7000
        self.p1.save()

        self.p2.points = 20
        self.p2.answered_count = 2
        self.p2.total_answer_time_ms = 7000
        self.p2.save()

        self.p3.points = 10
        self.p3.answered_count = 3
        self.p3.total_answer_time_ms = 1000
        self.p3.save()

        self.session.current_status = GameSession.Status.GAME_OVER
        self.session.question_asked_count = self.session.session_questions.count()
        self.session.save()

        GameService(self.session).end_game_session()
        self.session.refresh_from_db()

        self.assertEqual(self.session.winner_id, self.p1.id)