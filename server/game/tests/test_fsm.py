from django.test import TestCase
from statemachine.exceptions import TransitionNotAllowed
from game.models import GameSession, SessionPlayer, Question, SessionQuestion


class GameStateMachineTests(TestCase):
	def setUp(self):
		self.session = GameSession.objects.create()

		self.player1 = SessionPlayer.objects.create(
			session=self.session,
			display_name="Player 1",
			seat_number=1,
			lives=3,
		)
		self.player2 = SessionPlayer.objects.create(
			session=self.session,
			display_name="Player 2",
			seat_number=2,
			lives=3,
		)

		self.question1 = Question.objects.create(
			question_text="2 + 2?",
			correct_answer="4",
		)
		self.question2 = Question.objects.create(
			question_text="Capital of Poland?",
			correct_answer="Warsaw",
		)

		SessionQuestion.objects.create(
			session=self.session,
			question=self.question1,
			order_index=0,
		)
		SessionQuestion.objects.create(
			session=self.session,
			question=self.question2,
			order_index=1,
		)

	def test_initial_state_is_lobby(self):
		self.assertEqual(self.session.current_status, GameSession.Status.LOBBY)

	def test_start_game_transitions_from_lobby_to_answering(self):
		self.session.fsm.start_game()
		self.session.save()

		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)

	def test_submit_answer_transitions_from_answering_to_evaluation(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.save()

		self.session.fsm.submit_answer()
		self.session.save()

		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.EVALUATION)

	def test_resolve_evaluation_goes_to_game_over_when_one_player_alive(self):
		self.session.current_status = GameSession.Status.EVALUATION
		self.session.question_asked_count = 0
		self.session.save()

		self.player2.lives = 0
		self.player2.save()

		self.session.fsm.resolve_evaluation()
		self.session.save()

		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.GAME_OVER)

	def test_resolve_evaluation_goes_to_game_over_when_questions_exhausted(self):
		self.session.current_status = GameSession.Status.EVALUATION
		self.session.question_asked_count = self.session.session_questions.count()
		self.session.save()

		self.session.fsm.resolve_evaluation()
		self.session.save()

		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.GAME_OVER)

	def test_resolve_evaluation_goes_to_nomination_when_last_correct_player_alive(self):
		self.session.current_status = GameSession.Status.EVALUATION
		self.session.last_correct_player = self.player1
		self.session.question_asked_count = 0
		self.session.save()

		self.session.fsm.resolve_evaluation()
		self.session.save()

		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)

	def test_resolve_evaluation_goes_to_answering_when_no_last_correct_player(self):
		self.session.current_status = GameSession.Status.EVALUATION
		self.session.last_correct_player = None
		self.session.question_asked_count = 0
		self.session.save()

		self.session.fsm.resolve_evaluation()
		self.session.save()

		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)

	def test_resolve_evaluation_goes_to_answering_when_last_correct_player_dead(self):
		self.player3 = SessionPlayer.objects.create(
			session=self.session,
			display_name="Player 3",
			seat_number=3,
			lives=3,
		)
				
		self.session.current_status = GameSession.Status.EVALUATION
		self.session.last_correct_player = self.player1
		self.session.question_asked_count = 0
		self.session.save()

		self.player1.lives = 0
		self.player1.save()

		self.session.fsm.resolve_evaluation()
		self.session.save()

		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)

	def test_resolve_evaluation_prioritizes_game_over_over_nomination(self):
		self.session.current_status = GameSession.Status.EVALUATION
		self.session.last_correct_player = self.player1
		self.session.question_asked_count = self.session.session_questions.count()
		self.session.save()

		self.session.fsm.resolve_evaluation()
		self.session.save()

		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.GAME_OVER)

	def test_nominate_player_transitions_from_nomination_to_answering(self):
		self.session.current_status = GameSession.Status.NOMINATION
		self.session.save()

		self.session.fsm.nominate_player()
		self.session.save()

		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)

	def test_cancel_game_from_lobby_transitions_to_game_over(self):
		self.session.fsm.cancel_game()
		self.session.save()
		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.GAME_OVER)

	def test_cancel_game_from_answering_transitions_to_game_over(self):
		self.session.current_status = GameSession.Status.ANSWERING
		self.session.save()
		self.session.fsm.cancel_game()
		self.session.save()
		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.GAME_OVER)

	def test_cancel_game_from_evaluation_transitions_to_game_over(self):
		self.session.current_status = GameSession.Status.EVALUATION
		self.session.save()
		self.session.fsm.cancel_game()
		self.session.save()
		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.GAME_OVER)

	def test_cancel_game_from_nomination_transitions_to_game_over(self):
		self.session.current_status = GameSession.Status.NOMINATION
		self.session.save()
		self.session.fsm.cancel_game()
		self.session.save()
		self.session.refresh_from_db()
		self.assertEqual(self.session.current_status, GameSession.Status.GAME_OVER)
		
	def test_invalid_transitions_are_blocked_by_fsm(self):
		self.session.current_status = GameSession.Status.LOBBY
		self.session.save()

		with self.assertRaises(TransitionNotAllowed):
			self.session.fsm.submit_answer()
			
		with self.assertRaises(TransitionNotAllowed):
			self.session.fsm.nominate_player()

	def test_has_last_correct_player_alive_returns_false_without_last_correct_player(self):
		self.session.last_correct_player = None
		self.session.save()

		self.assertFalse(self.session.fsm.has_last_correct_player_alive())

	def test_has_last_correct_player_alive_returns_true_when_player_alive(self):
		self.session.last_correct_player = self.player1
		self.session.save()

		self.assertTrue(self.session.fsm.has_last_correct_player_alive())

	def test_has_last_correct_player_alive_returns_false_when_player_dead(self):
		self.session.last_correct_player = self.player1
		self.session.save()

		self.player1.lives = 0
		self.player1.save()

		self.assertFalse(self.session.fsm.has_last_correct_player_alive())

	def test_is_game_over_returns_false_when_multiple_players_alive_and_questions_available(self):
		self.session.question_asked_count = 0
		self.session.save()

		self.assertFalse(self.session.fsm.is_game_over())

	def test_is_game_over_returns_true_when_only_one_player_alive(self):
		self.player2.lives = 0
		self.player2.save()

		self.assertTrue(self.session.fsm.is_game_over())

	def test_is_game_over_returns_true_when_questions_exhausted(self):
		self.session.question_asked_count = self.session.session_questions.count()
		self.session.save()

		self.assertTrue(self.session.fsm.is_game_over())