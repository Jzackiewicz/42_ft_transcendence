from django.test import TestCase
from django.utils import timezone

from game.models import GameSession, SessionPlayer, Question, SessionQuestion, AnswerAttempt


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

        self.sq1 = SessionQuestion.objects.create(session=self.session, question=q1, order_index=0)
        self.sq2 = SessionQuestion.objects.create(session=self.session, question=q2, order_index=1)
        self.sq3 = SessionQuestion.objects.create(session=self.session, question=q3, order_index=2)

        self.session.refresh_from_db()
        self.fsm = self.session.fsm

    def _save_and_refresh_session(self):
        self.session.save()
        self.session.refresh_from_db()

    def _start_game(self, starting_player=None):
        starting_player = starting_player or self.p1
        self.fsm.start_game(starting_player_id=starting_player.id)
        self._save_and_refresh_session()

    def _set_current_attempt(self, *, player=None, session_question=None, is_correct=None):
        player = player or self.session.current_player
        session_question = session_question or self.session.current_question

        attempt = AnswerAttempt.objects.create(
            session=self.session,
            player=player,
            session_question=session_question,
            answer_text="dummy",
            is_timeout=False,
            is_correct=is_correct,
            evaluation_status=AnswerAttempt.EvaluationStatus.PENDING,
            answer_time_ms=1000,
            started_at=timezone.now(),
        )
        self.session.current_attempt = attempt
        self.session.save()
        self.session.refresh_from_db()
        return attempt

    def test_start_game_sets_initial_state(self):
        self._start_game()

        self.assertEqual(self.session.current_player, self.p1)
        self.assertEqual(self.session.current_question, self.sq1)
        self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
        self.assertIsNone(self.session.last_correct_player)
        self.assertIsNone(self.session.last_nominated_player)

    def test_mark_correct_adds_points_and_sets_last_correct_player(self):
        self._start_game()
        self._set_current_attempt(player=self.p1, session_question=self.sq1, is_correct=True)

        self.fsm.submit_answer()
        self.session.save()

        self.fsm.mark_correct()
        self.session.save()

        self.fsm.resolve_evaluation()
        self._save_and_refresh_session()
        self.p1.refresh_from_db()

        self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)
        self.assertEqual(self.session.last_correct_player, self.p1)
        self.assertEqual(self.p1.points, 10)
        self.assertEqual(self.p1.answered_count, 1)

    def test_mark_wrong_decrements_life_and_falls_back_without_last_correct_player(self):
        self._start_game()
        self._set_current_attempt(player=self.p1, session_question=self.sq1, is_correct=False)

        self.fsm.submit_answer()
        self.session.save()

        self.fsm.mark_wrong()
        self.session.save()

        self.fsm.resolve_evaluation()
        self._save_and_refresh_session()
        self.p1.refresh_from_db()

        self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
        self.assertEqual(self.session.current_player, self.p2)
        self.assertEqual(self.session.current_question, self.sq2)
        self.assertEqual(self.p1.lives, 2)
        self.assertEqual(self.p1.answered_count, 1)

    def test_self_nomination_and_correct_answer_gives_twenty_bonus(self):
        self._start_game()

        self._set_current_attempt(player=self.p1, session_question=self.sq1, is_correct=True)
        self.fsm.submit_answer()
        self.session.save()
        self.fsm.mark_correct()
        self.session.save()
        self.fsm.resolve_evaluation()
        self._save_and_refresh_session()

        self.fsm.nominate_player(target_player_id=self.p1.id)
        self._save_and_refresh_session()

        self.assertEqual(self.session.current_player, self.p1)
        self.assertEqual(self.session.current_question, self.sq2)
        self.assertEqual(self.session.last_nominated_player, self.p1)

        self._set_current_attempt(player=self.p1, session_question=self.sq2, is_correct=True)
        self.fsm.submit_answer()
        self.session.save()
        self.fsm.mark_correct()
        self.session.save()
        self.fsm.resolve_evaluation()
        self._save_and_refresh_session()
        self.p1.refresh_from_db()

        self.assertEqual(self.p1.points, 30)  # 10 + 20
        self.assertEqual(self.session.last_correct_player, self.p1)
        self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)

    def test_wrong_answer_with_alive_last_correct_player_returns_to_nomination(self):
        self._start_game()

        self._set_current_attempt(player=self.p1, session_question=self.sq1, is_correct=True)
        self.fsm.submit_answer()
        self.session.save()
        self.fsm.mark_correct()
        self.session.save()
        self.fsm.resolve_evaluation()
        self._save_and_refresh_session()

        self.fsm.nominate_player(target_player_id=self.p2.id)
        self._save_and_refresh_session()

        self._set_current_attempt(player=self.p2, session_question=self.sq2, is_correct=False)
        self.fsm.submit_answer()
        self.session.save()
        self.fsm.mark_wrong()
        self.session.save()
        self.fsm.resolve_evaluation()
        self._save_and_refresh_session()
        self.p2.refresh_from_db()

        self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)
        self.assertEqual(self.session.last_correct_player, self.p1)
        self.assertEqual(self.p2.lives, 2)

    def test_cannot_nominate_dead_player(self):
        self._start_game()
        self.p2.lives = 0
        self.p2.save()

        self._set_current_attempt(player=self.p1, session_question=self.sq1, is_correct=True)
        self.fsm.submit_answer()
        self.session.save()
        self.fsm.mark_correct()
        self.session.save()
        self.fsm.resolve_evaluation()
        self._save_and_refresh_session()

        with self.assertRaises(ValueError):
            self.fsm.nominate_player(target_player_id=self.p2.id)

    def test_game_ends_when_only_one_player_remains_alive(self):
        self.p1.lives = 1
        self.p1.save()
        self.p2.lives = 0
        self.p2.save()
        self.p3.lives = 3
        self.p3.save()

        self._start_game(starting_player=self.p1)
        self._set_current_attempt(player=self.p1, session_question=self.sq1, is_correct=False)

        self.fsm.submit_answer()
        self.session.save()
        self.fsm.mark_wrong()
        self.session.save()
        self.fsm.resolve_evaluation()
        self._save_and_refresh_session()
        self.p1.refresh_from_db()

        self.assertEqual(self.p1.lives, 0)
        self.assertEqual(self.session.current_status, GameSession.Status.GAME_OVER)

    def test_correct_answer_on_last_question_ends_game(self):
        self._start_game()

        self._set_current_attempt(player=self.p1, session_question=self.sq1, is_correct=True)
        self.fsm.submit_answer()
        self.session.save()
        self.fsm.mark_correct()
        self.session.save()
        self.fsm.resolve_evaluation()
        self._save_and_refresh_session()

        self.fsm.nominate_player(target_player_id=self.p2.id)
        self._save_and_refresh_session()

        self._set_current_attempt(player=self.p2, session_question=self.sq2, is_correct=True)
        self.fsm.submit_answer()
        self.session.save()
        self.fsm.mark_correct()
        self.session.save()
        self.fsm.resolve_evaluation()
        self._save_and_refresh_session()

        self.fsm.nominate_player(target_player_id=self.p3.id)
        self._save_and_refresh_session()

        self._set_current_attempt(player=self.p3, session_question=self.sq3, is_correct=True)
        self.fsm.submit_answer()
        self.session.save()
        self.fsm.mark_correct()
        self.session.save()
        self.fsm.resolve_evaluation()
        self._save_and_refresh_session()

        self.assertEqual(self.session.current_status, GameSession.Status.GAME_OVER)

    def test_wrong_answer_with_dead_last_correct_player_falls_back_to_next_alive_player(self):
        self._start_game()

        self._set_current_attempt(player=self.p1, session_question=self.sq1, is_correct=True)
        self.fsm.submit_answer()
        self.session.save()
        self.fsm.mark_correct()
        self.session.save()
        self.fsm.resolve_evaluation()
        self._save_and_refresh_session()

        self.p1.lives = 0
        self.p1.save()

        self.fsm.nominate_player(target_player_id=self.p2.id)
        self._save_and_refresh_session()

        self._set_current_attempt(player=self.p2, session_question=self.sq2, is_correct=False)
        self.fsm.submit_answer()
        self.session.save()
        self.fsm.mark_wrong()
        self.session.save()
        self.fsm.resolve_evaluation()
        self._save_and_refresh_session()
        self.p2.refresh_from_db()

        self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
        self.assertEqual(self.session.current_player, self.p3)
        self.assertEqual(self.session.current_question, self.sq3)
        self.assertEqual(self.p2.lives, 2)