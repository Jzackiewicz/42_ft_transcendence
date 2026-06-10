from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError

from game.models import (
	AnswerAttempt,
	GameSession,
	Question,
	SessionPlayer,
	SessionQuestion,
)
from game.services.game_flow.game_service import GameService
from game.services.game_flow.lifecycle import set_end_game_stats


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

		self.session.host_player = self.p1
		self.session.save()

	def refresh(self):
		self.session.refresh_from_db()
		self.p1.refresh_from_db()
		self.p2.refresh_from_db()
		self.p3.refresh_from_db()

	def test_start_game_moves_to_answering_and_creates_attempt(self):
		GameService(self.session).start_game_session(actor=self.p1)
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

		with self.assertRaisesMessage(ValidationError, "Game session is not in lobby state"):
			GameService(self.session).start_game_session(actor=self.p1)

	def test_start_game_requires_at_least_two_players(self):
		self.p2.delete()
		self.p3.delete()

		with self.assertRaisesMessage(
			ValidationError,
			"Cannot start game with fewer than 2 players",
		):
			GameService(self.session).start_game_session(actor=self.p1)

	def test_start_game_requires_questions(self):
		self.session.session_questions.all().delete()
		Question.objects.all().delete()

		with self.assertRaisesMessage(
			ValidationError,
			"Cannot start game without questions in the database.",
		):
			GameService(self.session).start_game_session(actor=self.p1)

	def test_start_game_fails_if_not_enough_questions(self):
		self.session.session_questions.all().delete()

		with self.assertRaisesMessage(
			ValidationError,
			"Not enough questions. Required: 10, available: 4.",
		):
			GameService(self.session).start_game_session(actor=self.p1)

	def test_start_game_rejects_non_host(self):
		with self.assertRaisesMessage(ValidationError, "Only the host can start the game"):
			GameService(self.session).start_game_session(actor=self.p2)

	def test_submit_answer_by_current_player_moves_to_evaluation(self):
		GameService(self.session).start_game_session(actor=self.p1)
		self.session.refresh_from_db()

		actor = self.session.current_player
		old_attempt_id = self.session.current_attempt_id

		GameService(self.session).submit_player_answer(actor=actor, answer="4")
		self.session.refresh_from_db()

		attempt = AnswerAttempt.objects.get(id=old_attempt_id)

		self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)
		self.assertEqual(attempt.answer_text, "4")
		self.assertFalse(attempt.is_timeout)
		self.assertTrue(attempt.is_correct)
		self.assertGreaterEqual(attempt.answer_time_ms, 0)

		# Complete evaluation to transition
		GameService(self.session).resolve_evaluation()
		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)

	def test_submit_answer_rejects_non_current_player(self):
		GameService(self.session).start_game_session(actor=self.p1)
		self.session.refresh_from_db()

		actor = self.session.session_players.exclude(
			id=self.session.current_player_id
		).first()

		with self.assertRaisesMessage(ValidationError, "Only current player can submit answer"):
			GameService(self.session).submit_player_answer(actor=actor, answer="4")

	def test_submit_answer_timeout_ignores_answer_text_and_evaluates_wrong(self):
		GameService(self.session).start_game_session(actor=self.p1)
		self.session.refresh_from_db()

		attempt = self.session.current_attempt
		attempt.started_at = timezone.now() - timedelta(seconds=30)
		attempt.save()

		actor = self.session.current_player
		old_attempt_id = attempt.id

		GameService(self.session).submit_player_answer(actor=actor, answer="4")
		self.session.refresh_from_db()

		attempt = AnswerAttempt.objects.get(id=old_attempt_id)

		self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)
		self.assertTrue(attempt.is_timeout)
		self.assertIsNone(attempt.answer_text)
		self.assertFalse(attempt.is_correct)

		# Complete evaluation to transition
		GameService(self.session).resolve_evaluation()
		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)

	def test_submit_correct_answer_adds_points_and_goes_to_nomination(self):
		GameService(self.session).start_game_session(actor=self.p1)
		self.session.refresh_from_db()

		actor = self.session.current_player
		correct_answer = self.session.current_question.question.correct_answer

		GameService(self.session).submit_player_answer(
			actor=actor,
			answer=correct_answer,
		)
		self.session.refresh_from_db()

		actor.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)
		self.assertEqual(self.session.last_correct_player_id, actor.id)
		self.assertEqual(actor.points, 10)
		self.assertEqual(actor.answered_count, 1)

		# Complete evaluation to transition
		GameService(self.session).resolve_evaluation()
		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)
		self.assertIsNone(self.session.current_attempt)

	def test_evaluate_correct_answer_gives_20_points_if_player_self_nominated(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p2
		self.session.last_nominated_player = self.p2
		self.session.last_correct_player = self.p2
		self.session.save()

		GameService(self.session)._start_answering_turn()
		self.session.refresh_from_db()

		GameService(self.session).submit_player_answer(actor=self.p2, answer="4")
		self.session.refresh_from_db()

		self.p2.refresh_from_db()

		self.assertEqual(self.p2.points, 20)

	def test_evaluate_correct_answer_gives_10_points_if_nominated_by_other(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p2
		self.session.last_nominated_player = self.p2
		self.session.last_correct_player = self.p1
		self.session.save()

		GameService(self.session)._start_answering_turn()
		self.session.refresh_from_db()

		GameService(self.session).submit_player_answer(actor=self.p2, answer="4")
		self.session.refresh_from_db()

		self.p2.refresh_from_db()

		self.assertEqual(self.p2.points, 10)

	def test_wrong_answer_without_last_correct_player_fallbacks_to_next_alive_player_and_starts_new_attempt(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p1
		self.session.save()

		GameService(self.session)._start_answering_turn()
		self.session.refresh_from_db()

		old_attempt_id = self.session.current_attempt_id

		GameService(self.session).submit_player_answer(actor=self.p1, answer="wrong")
		self.session.refresh_from_db()

		self.p1.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)
		self.assertEqual(self.p1.lives, 2)

		# Complete evaluation to transition
		GameService(self.session).resolve_evaluation()
		self.session.refresh_from_db()
		self.p1.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
		self.assertEqual(self.session.current_player_id, self.p2.id)
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

		self.p2.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)
		self.assertEqual(self.p2.lives, 2)

		# Complete evaluation to transition
		GameService(self.session).resolve_evaluation()
		self.session.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)
		self.assertEqual(self.session.last_correct_player_id, self.p1.id)
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

		with self.assertRaisesMessage(ValidationError, "Only last correct player can nominate"):
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

		with self.assertRaisesMessage(ValidationError, "Cannot nominate a dead player"):
			GameService(self.session).nominate_player(
				actor=self.p1,
				target_player_id=self.p3.id,
			)

	def test_disconnect_that_leaves_one_player_ends_game(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p2
		self.session.save()
		GameService(self.session)._start_answering_turn()

		self.p3.lives = 0
		self.p3.save()

		# p2 disconnects, leaving only p1 alive
		GameService(self.session).disconnect_player(actor=self.p2)
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

		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p3
		self.session.question_asked_count = self.session.session_questions.count() - 1
		self.session.save()

		set_end_game_stats(self.session)
		GameService(self.session)._start_answering_turn()
		self.session.refresh_from_db()

		GameService(self.session).submit_player_answer(actor=self.p3, answer="wrong")
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

		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p3
		self.session.question_asked_count = self.session.session_questions.count() - 1
		self.session.save()

		set_end_game_stats(self.session)
		GameService(self.session)._start_answering_turn()
		self.session.refresh_from_db()

		GameService(self.session).submit_player_answer(actor=self.p3, answer="wrong")
		self.session.refresh_from_db()

		self.assertEqual(self.session.winner_id, self.p1.id)

	def test_submit_answer_requires_active_attempt(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p1
		self.session.current_question = self.sq1
		self.session.current_attempt = None
		self.session.save()

		with self.assertRaises(ValidationError):
			GameService(self.session).submit_player_answer(
				actor=self.p1,
				answer="4",
			)

	def test_submit_answer_rejects_non_pending_attempt(self):
		attempt = AnswerAttempt.objects.create(
			session=self.session,
			player=self.p1,
			session_question=self.sq1,
			answer_text="4",
			is_timeout=False,
			is_correct=True,
			evaluation_status=AnswerAttempt.EvaluationStatus.EVALUATED,
			answer_time_ms=1000,
			started_at=timezone.now(),
			evaluated_at=timezone.now(),
		)

		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p1
		self.session.current_question = self.sq1
		self.session.current_attempt = attempt
		self.session.save()

		with self.assertRaises(ValidationError):
			GameService(self.session).submit_player_answer(
				actor=self.p1,
				answer="4",
			)
			
	def test_evaluate_answer_requires_current_attempt(self):
		self.session.current_status = GameSession.Status.EVALUATION
		self.session.current_attempt = None
		self.session.save()

		with self.assertRaises(ValidationError):
			GameService(self.session).start_evaluation()

	def test_timeout_answer_is_evaluated_as_wrong_and_fallbacks(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p1
		self.session.save()

		GameService(self.session)._start_answering_turn()
		self.session.refresh_from_db()

		old_attempt_id = self.session.current_attempt_id

		attempt = self.session.current_attempt
		attempt.started_at = timezone.now() - timedelta(seconds=30)
		attempt.save()

		GameService(self.session).submit_player_answer(
			actor=self.p1,
			answer="4",
		)
		self.session.refresh_from_db()

		self.p1.refresh_from_db()

		old_attempt = AnswerAttempt.objects.get(id=old_attempt_id)

		self.assertTrue(old_attempt.is_timeout)
		self.assertFalse(old_attempt.is_correct)
		self.assertEqual(self.p1.lives, 2)
		self.assertEqual(self.p1.answered_count, 1)
		self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)

		# Complete evaluation to transition
		GameService(self.session).resolve_evaluation()
		self.session.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
		self.assertEqual(self.session.current_player_id, self.p2.id)
		self.assertIsNotNone(self.session.current_attempt)
		self.assertNotEqual(self.session.current_attempt_id, old_attempt_id)
		
	def test_evaluate_timeout_is_processed_correctly_when_no_answer_submitted(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p1
		self.session.save()

		GameService(self.session)._start_answering_turn()
		self.session.refresh_from_db()
		
		old_attempt_id = self.session.current_attempt_id

		attempt = self.session.current_attempt
		attempt.started_at = timezone.now() - timedelta(seconds=30)
		attempt.save()

		GameService(self.session).evaluate_timeout()
		self.session.refresh_from_db()
		self.p1.refresh_from_db()
		
		old_attempt = AnswerAttempt.objects.get(id=old_attempt_id)
		
		self.assertTrue(old_attempt.is_timeout)
		self.assertFalse(old_attempt.is_correct)
		self.assertEqual(self.p1.lives, 2)
		self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)

		# Complete evaluation to transition
		GameService(self.session).resolve_evaluation()
		self.session.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
		self.assertEqual(self.session.current_player_id, self.p2.id)

	def test_wrong_answer_that_eliminates_player_ends_game_through_evaluation_flow(self):
		self.p2.lives = 1
		self.p2.save()

		self.p3.lives = 0
		self.p3.save()

		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p2
		self.session.save()

		GameService(self.session)._start_answering_turn()
		self.session.refresh_from_db()

		GameService(self.session).submit_player_answer(
			actor=self.p2,
			answer="wrong",
		)
		self.session.refresh_from_db()

		self.p2.refresh_from_db()

		self.assertEqual(self.p2.lives, 0)
		self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)

		# Complete evaluation to transition
		GameService(self.session).resolve_evaluation()
		self.session.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.GAME_OVER)
		self.assertEqual(self.session.winner_id, self.p1.id)
		self.assertEqual(
			self.session.end_reason,
			GameSession.EndReason.LAST_PLAYER_ALIVE,
		)
		self.assertIsNotNone(self.session.ended_at)
		self.assertIsNone(self.session.current_attempt)
		self.assertIsNone(self.session.current_question)

	def test_questions_exhausted_ends_game_through_evaluation_flow(self):
		total_questions = self.session.session_questions.count()

		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p1
		self.session.question_asked_count = total_questions - 1
		self.session.save()

		GameService(self.session)._start_answering_turn()
		self.session.refresh_from_db()

		correct_answer = self.session.current_question.question.correct_answer

		GameService(self.session).submit_player_answer(
			actor=self.p1,
			answer=correct_answer,
		)
		self.session.refresh_from_db()

		self.p1.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)

		# Complete evaluation to transition
		GameService(self.session).resolve_evaluation()
		self.session.refresh_from_db()

		self.assertEqual(self.session.question_asked_count, total_questions)
		self.assertEqual(self.session.current_status, GameSession.Status.GAME_OVER)
		self.assertEqual(
			self.session.end_reason,
			GameSession.EndReason.QUESTIONS_EXHAUSTED,
		)
		self.assertEqual(self.session.winner_id, self.p1.id)
		self.assertIsNotNone(self.session.ended_at)
		self.assertIsNone(self.session.current_attempt)
		self.assertIsNone(self.session.current_question)

	def test_nominate_player_requires_nomination_state(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.last_correct_player = self.p1
		self.session.current_player = self.p1
		self.session.save()

		with self.assertRaises(ValidationError):
			GameService(self.session).nominate_player(
				actor=self.p1,
				target_player_id=self.p2.id,
			)

	def test_disconnect_in_lobby_shifts_host_to_oldest_player(self):
		self.session.current_status = GameSession.Status.LOBBY
		self.session.host_player = self.p1
		self.session.save()

		GameService(self.session).disconnect_player(self.p1)
		self.session.refresh_from_db()

		# p1 is deleted, host is shifted to p2 (lower ID than p3)
		self.assertFalse(SessionPlayer.objects.filter(id=self.p1.id).exists())
		self.assertEqual(self.session.host_player_id, self.p2.id)

	def test_disconnect_in_lobby_deletes_session_if_last_player(self):
		self.session.current_status = GameSession.Status.LOBBY
		self.session.host_player = self.p1
		self.session.save()
		
		self.p2.delete()
		self.p3.delete()

		GameService(self.session).disconnect_player(self.p1)
		self.assertFalse(GameSession.objects.filter(id=self.session.id).exists())

	def test_disconnect_in_answering_by_current_player_advances_turn(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p1
		self.session.save()
		GameService(self.session)._start_answering_turn()
		self.session.refresh_from_db()

		old_attempt_id = self.session.current_attempt_id

		GameService(self.session).disconnect_player(self.p1)
		self.session.refresh_from_db()
		self.p1.refresh_from_db()

		self.assertEqual(self.p1.lives, 0)
		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
		self.assertEqual(self.session.current_player_id, self.p2.id)
		self.assertNotEqual(self.session.current_attempt_id, old_attempt_id)

	def test_disconnect_in_nomination_auto_nominates_and_advances(self):
		self.session.current_status = GameSession.Status.NOMINATION
		self.session.last_correct_player = self.p1
		self.session.current_player = self.p1
		self.session.save()

		GameService(self.session).disconnect_player(self.p1)
		self.session.refresh_from_db()
		self.p1.refresh_from_db()

		self.assertEqual(self.p1.lives, 0)
		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
		self.assertIn(self.session.current_player_id, [self.p2.id, self.p3.id])
		self.assertIsNotNone(self.session.current_attempt)

	def test_disconnect_by_observer_does_not_affect_game_state(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p2
		self.session.save()
		GameService(self.session)._start_answering_turn()
		self.session.refresh_from_db()
		
		old_attempt_id = self.session.current_attempt_id

		# p1 (not their turn) disconnects
		GameService(self.session).disconnect_player(self.p1)
		self.session.refresh_from_db()
		self.p1.refresh_from_db()

		self.assertEqual(self.p1.lives, 0)
		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
		self.assertEqual(self.session.current_player_id, self.p2.id)
		self.assertEqual(self.session.current_attempt_id, old_attempt_id)

	def test_disconnect_in_game_over_does_nothing(self):
		self.session.current_status = GameSession.Status.GAME_OVER
		self.session.save()

		GameService(self.session).disconnect_player(self.p1)
		self.p1.refresh_from_db()
		
		self.assertEqual(self.p1.lives, 3)

	def test_wrong_answer_fallbacks_and_skips_dead_player_in_queue(self):
		self.p2.lives = 0
		self.p2.save()

		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p1
		self.session.save()

		GameService(self.session)._start_answering_turn()
		self.session.refresh_from_db()

		GameService(self.session).submit_player_answer(actor=self.p1, answer="wrong")
		self.session.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)

		# Complete evaluation to transition
		GameService(self.session).resolve_evaluation()
		self.session.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
		self.assertEqual(self.session.current_player_id, self.p3.id)

	def test_evaluate_correct_answer_ignores_case_and_trailing_whitespaces(self):
		self.q1.correct_answer = "Paris"
		self.q1.save()
		
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p1
		self.session.save()

		GameService(self.session)._start_answering_turn()
		self.session.refresh_from_db()

		GameService(self.session).submit_player_answer(actor=self.p1, answer="  pArIs ")
		self.session.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)
		self.assertEqual(self.session.last_correct_player_id, self.p1.id)

		# Complete evaluation to transition
		GameService(self.session).resolve_evaluation()
		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)

	def test_last_correct_player_loses_status_if_dead_after_evaluation(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p2
		self.session.last_correct_player = self.p1
		self.session.save()
		
		self.p1.lives = 0
		self.p1.save()

		GameService(self.session)._start_answering_turn()
		self.session.refresh_from_db()

		GameService(self.session).submit_player_answer(actor=self.p2, answer="wrong")
		self.session.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)

		# Complete evaluation to transition
		GameService(self.session).resolve_evaluation()
		self.session.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
		self.assertEqual(self.session.current_player_id, self.p3.id)

	def test_nominate_requires_target_player_id(self):
		self.session.current_status = GameSession.Status.NOMINATION
		self.session.last_correct_player = self.p1
		self.session.current_player = self.p1
		self.session.save()

		with self.assertRaises(ValidationError):
			GameService(self.session).nominate_player(
				actor=self.p1,
				target_player_id=None,
			)

	def test_nominate_self(self):
		self.session.current_status = GameSession.Status.NOMINATION
		self.session.last_correct_player = self.p1
		self.session.current_player = self.p1
		self.session.save()

		GameService(self.session).nominate_player(
			actor=self.p1,
			target_player_id=self.p1.id,
		)
		self.session.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
		self.assertEqual(self.session.current_player_id, self.p1.id)

	def test_disconnect_in_evaluation_does_not_break_flow(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.current_player = self.p1
		self.session.save()

		GameService(self.session)._start_answering_turn()
		self.session.refresh_from_db()

		GameService(self.session).submit_player_answer(actor=self.p1, answer="4")
		self.session.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)

		# resolve_evaluation to transition
		GameService(self.session).resolve_evaluation()
		self.session.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)

		GameService(self.session).disconnect_player(self.p3)
		self.session.refresh_from_db()
		self.p3.refresh_from_db()

		self.assertEqual(self.p3.lives, 0)
		self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)

	def test_start_game_requires_actor(self):
		with self.assertRaises(ValidationError):
			GameService(self.session).start_game_session(actor=None)


from game.serializers import GameStateSnapshotSerializer

class GameStateSnapshotTests(TestCase):
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
		self.q1 = Question.objects.create(
			question_text="2 + 2?",
			correct_answer="4",
			category="math",
		)
		self.sq1 = SessionQuestion.objects.create(
			session=self.session,
			question=self.q1,
			order_index=0,
		)
		self.session.current_player = self.p1
		self.session.current_question = self.sq1
		self.session.save()

	def test_snapshot_answering_phase_hides_correct_answer(self):
		self.session.current_status = GameSession.Status.ANSWERING
		attempt = AnswerAttempt.objects.create(
			session=self.session,
			player=self.p1,
			session_question=self.sq1,
			started_at=timezone.now(),
		)
		self.session.current_attempt = attempt
		self.session.save()

		serializer = GameStateSnapshotSerializer(self.session)
		data = serializer.data

		self.assertEqual(data["current_status"], "answering")
		self.assertIsNotNone(data["current_attempt"])
		self.assertIsNone(data["current_attempt"]["correct_answer"])
		self.assertEqual(data["current_attempt"]["evaluation_status"], "pending")

	def test_snapshot_evaluation_phase_reveals_correct_answer(self):
		self.session.current_status = GameSession.Status.EVALUATION
		attempt = AnswerAttempt.objects.create(
			session=self.session,
			player=self.p1,
			session_question=self.sq1,
			answer_text="4",
			is_correct=True,
			evaluation_status=AnswerAttempt.EvaluationStatus.EVALUATED,
			started_at=timezone.now(),
			evaluated_at=timezone.now(),
		)
		self.session.current_attempt = attempt
		self.session.save()

		serializer = GameStateSnapshotSerializer(self.session)
		data = serializer.data

		self.assertEqual(data["current_status"], "evaluation")
		self.assertIsNotNone(data["current_attempt"])
		self.assertEqual(data["current_attempt"]["correct_answer"], "4")
		self.assertEqual(data["current_attempt"]["evaluation_status"], "evaluated")

	def test_snapshot_other_phase_with_evaluated_attempt_hides_correct_answer(self):
		# Safe measure: even if evaluation_status is EVALUATED, if state is not EVALUATION, hide correct answer
		self.session.current_status = GameSession.Status.NOMINATION
		attempt = AnswerAttempt.objects.create(
			session=self.session,
			player=self.p1,
			session_question=self.sq1,
			answer_text="4",
			is_correct=True,
			evaluation_status=AnswerAttempt.EvaluationStatus.EVALUATED,
			started_at=timezone.now(),
			evaluated_at=timezone.now(),
		)
		self.session.current_attempt = attempt
		self.session.save()

		serializer = GameStateSnapshotSerializer(self.session)
		data = serializer.data

		self.assertEqual(data["current_status"], "nomination")
		self.assertIsNotNone(data["current_attempt"])
		self.assertIsNone(data["current_attempt"]["correct_answer"])

	def test_nominate_timeout_selects_random_player(self):
		self.session.current_status = GameSession.Status.NOMINATION
		self.session.last_correct_player = self.p1
		self.session.current_player = self.p1
		self.session.save()

		# Setup questions for the turn advance (self.sq1 is already created in setUp with self.q1)
		q2 = Question.objects.create(question_text="Q2", correct_answer="A2", category="cat")
		self.sq2 = SessionQuestion.objects.create(session=self.session, question=q2, order_index=1)

		GameService(self.session).nominate_timeout()
		self.session.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
		self.assertIn(self.session.current_player_id, [self.p1.id, self.p2.id])
		self.assertIsNotNone(self.session.current_attempt)

