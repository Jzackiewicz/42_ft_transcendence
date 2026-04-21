from django.test import TestCase
from game.models import GameSession, SessionPlayer, Question, SessionQuestion, AnswerAttempt


"""
These tests cover ONLY FSM logic and state transitions.
They do NOT test higher-level application/service orchestration (that will be covered in services.py)
"""


class FSMTestCase(TestCase):
    def setUp(self):
        self.session = GameSession.objects.create()

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
        self.p3 = SessionPlayer.objects.create(
            session=self.session,
            display_name="P3",
            seat_number=3,
        )

        q1 = Question.objects.create(question_text="Q1", correct_answer="A")
        q2 = Question.objects.create(question_text="Q2", correct_answer="B")
        q3 = Question.objects.create(question_text="Q3", correct_answer="C")

        SessionQuestion.objects.create(session=self.session, question=q1, order_index=0)
        SessionQuestion.objects.create(session=self.session, question=q2, order_index=1)
        SessionQuestion.objects.create(session=self.session, question=q3, order_index=2)

        self.session.refresh_from_db()
        self.fsm = self.session.fsm

    def _save_and_refresh_session(self):
        self.session.save()
        self.session.refresh_from_db()

    def _submit_correct_and_resolve(self, answer="A"):
        self.fsm.submit_answer(answer=answer, is_timeout=False)
        self.session.save()

        self.fsm.mark_correct()
        self.session.save()

        self.fsm.resolve_evaluation()
        self._save_and_refresh_session()

    def _submit_wrong_and_resolve(self, answer="wrong", is_timeout=False):
        self.fsm.submit_answer(answer=answer, is_timeout=is_timeout)
        self.session.save()

        self.fsm.mark_wrong()
        self.session.save()

        self.fsm.resolve_evaluation()
        self._save_and_refresh_session()

    def test_start_game_sets_initial_state(self):
        self.fsm.start_game(starting_player_id=self.p1.id)
        self._save_and_refresh_session()

        self.assertEqual(self.session.current_player, self.p1)
        self.assertIsNotNone(self.session.current_question)
        self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)

    def test_submit_answer_creates_pending_attempt(self):
        self.fsm.start_game(starting_player_id=self.p1.id)
        self.session.save()

        self.fsm.submit_answer(answer="A", is_timeout=False)
        self.session.save()

        attempt = AnswerAttempt.objects.latest("id")

        self.assertEqual(attempt.session, self.session)
        self.assertEqual(attempt.player, self.p1)
        self.assertEqual(attempt.session_question, self.session.current_question)
        self.assertEqual(attempt.answer_text, "A")
        self.assertFalse(attempt.is_timeout)
        self.assertIsNone(attempt.is_correct)
        self.assertEqual(attempt.evaluation_status, AnswerAttempt.EvaluationStatus.PENDING)

    def test_mark_correct_evaluates_attempt_as_correct(self):
        self.fsm.start_game(starting_player_id=self.p1.id)
        self.session.save()

        self.fsm.submit_answer(answer="A", is_timeout=False)
        self.session.save()

        self.fsm.mark_correct()
        self.session.save()

        attempt = AnswerAttempt.objects.latest("id")
        self.p1.refresh_from_db()

        self.assertEqual(attempt.player, self.p1)
        self.assertEqual(attempt.evaluation_status, AnswerAttempt.EvaluationStatus.EVALUATED)
        self.assertTrue(attempt.is_correct)
        self.assertEqual(self.p1.points, 10)
        self.assertEqual(self.p1.answered_count, 1)

    def test_mark_wrong_evaluates_attempt_as_wrong(self):
        self.fsm.start_game(starting_player_id=self.p1.id)
        self.session.save()

        self.fsm.submit_answer(answer="wrong", is_timeout=False)
        self.session.save()

        self.fsm.mark_wrong()
        self.session.save()

        attempt = AnswerAttempt.objects.latest("id")
        self.p1.refresh_from_db()

        self.assertEqual(attempt.player, self.p1)
        self.assertEqual(attempt.evaluation_status, AnswerAttempt.EvaluationStatus.EVALUATED)
        self.assertFalse(attempt.is_correct)
        self.assertEqual(self.p1.lives, 2)
        self.assertEqual(self.p1.answered_count, 1)

    def test_correct_answer_sets_last_correct_player_and_enters_nomination(self):
        self.fsm.start_game(starting_player_id=self.p1.id)
        self.session.save()

        self._submit_correct_and_resolve(answer="A")
        self.p1.refresh_from_db()

        attempt = AnswerAttempt.objects.latest("id")

        self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)
        self.assertEqual(self.session.last_correct_player, self.p1)
        self.assertEqual(self.p1.points, 10)
        self.assertEqual(self.p1.answered_count, 1)
        self.assertEqual(attempt.evaluation_status, AnswerAttempt.EvaluationStatus.EVALUATED)
        self.assertTrue(attempt.is_correct)

    def test_wrong_answer_without_last_correct_player_falls_back_to_next_alive_player(self):
        self.fsm.start_game(starting_player_id=self.p1.id)
        self.session.save()

        self._submit_wrong_and_resolve(answer="wrong", is_timeout=False)
        self.p1.refresh_from_db()

        attempt = AnswerAttempt.objects.latest("id")

        self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
        self.assertEqual(self.session.current_player, self.p2)
        self.assertEqual(self.p1.lives, 2)
        self.assertEqual(self.p1.answered_count, 1)
        self.assertIsNotNone(self.session.current_question)
        self.assertEqual(attempt.evaluation_status, AnswerAttempt.EvaluationStatus.EVALUATED)
        self.assertFalse(attempt.is_correct)

    def test_self_nomination_and_correct_answer_gives_twenty_bonus(self):
        self.fsm.start_game(starting_player_id=self.p1.id)
        self.session.save()

        self._submit_correct_and_resolve(answer="A")

        self.fsm.nominate_player(target_player_id=self.p1.id)
        self._save_and_refresh_session()

        self.assertEqual(self.session.current_player, self.p1)
        self.assertEqual(self.session.last_nominated_player, self.p1)

        self._submit_correct_and_resolve(answer="A again")
        self.p1.refresh_from_db()

        self.assertEqual(self.p1.points, 30)  # 10 + 20
        self.assertEqual(self.session.last_correct_player, self.p1)
        self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)

    def test_wrong_answer_with_alive_last_correct_player_returns_to_nomination(self):
        self.fsm.start_game(starting_player_id=self.p1.id)
        self.session.save()

        self._submit_correct_and_resolve(answer="A")

        self.fsm.nominate_player(target_player_id=self.p2.id)
        self.session.save()

        self._submit_wrong_and_resolve(answer="wrong", is_timeout=False)
        self.p2.refresh_from_db()

        self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)
        self.assertEqual(self.session.last_correct_player, self.p1)
        self.assertEqual(self.p2.lives, 2)

    def test_timeout_is_treated_like_wrong_answer(self):
        self.fsm.start_game(starting_player_id=self.p1.id)
        self.session.save()

        self._submit_wrong_and_resolve(answer=None, is_timeout=True)
        self.p1.refresh_from_db()

        attempt = AnswerAttempt.objects.latest("id")

        self.assertEqual(self.p1.lives, 2)
        self.assertEqual(self.session.current_player, self.p2)
        self.assertTrue(attempt.is_timeout)
        self.assertFalse(attempt.is_correct)

    def test_cannot_nominate_dead_player(self):
        self.p2.lives = 0
        self.p2.save()

        self.fsm.start_game(starting_player_id=self.p1.id)
        self.session.save()

        self._submit_correct_and_resolve(answer="A")

        with self.assertRaises(ValueError):
            self.fsm.nominate_player(target_player_id=self.p2.id)

    def test_correct_answer_on_last_question_ends_game(self):
        self.fsm.start_game(starting_player_id=self.p1.id)
        self.session.save()

        self._submit_correct_and_resolve(answer="A")

        self.fsm.nominate_player(target_player_id=self.p2.id)
        self.session.save()
        self._submit_correct_and_resolve(answer="B")

        self.fsm.nominate_player(target_player_id=self.p3.id)
        self.session.save()
        self._submit_correct_and_resolve(answer="C")

        self.assertEqual(self.session.current_status, GameSession.Status.GAME_OVER)

    def test_game_ends_when_only_one_player_remains_alive(self):
        self.p1.lives = 1
        self.p1.save()

        self.p2.lives = 0
        self.p2.save()

        self.p3.lives = 3
        self.p3.save()

        self.fsm.start_game(starting_player_id=self.p1.id)
        self.session.save()

        self._submit_wrong_and_resolve(answer="wrong", is_timeout=False)
        self.p1.refresh_from_db()

        self.assertEqual(self.p1.lives, 0)
        self.assertEqual(self.session.current_status, GameSession.Status.GAME_OVER)

    def test_wrong_answer_with_dead_last_correct_player_falls_back_to_next_alive_player(self):
        self.fsm.start_game(starting_player_id=self.p1.id)
        self.session.save()

        self._submit_correct_and_resolve(answer="A")

        self.p1.lives = 0
        self.p1.save()

        self.fsm.nominate_player(target_player_id=self.p2.id)
        self.session.save()

        self._submit_wrong_and_resolve(answer="wrong", is_timeout=False)
        self.p2.refresh_from_db()

        self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
        self.assertEqual(self.session.current_player, self.p3)
        self.assertEqual(self.p2.lives, 2)