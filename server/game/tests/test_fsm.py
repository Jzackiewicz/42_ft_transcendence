from django.test import TestCase
from game.models import GameSession, SessionPlayer

class GameStateMachineTests(TestCase):

	def setUp(self):
		self.session = GameSession.objects.create(
			session_questions_ids=[101, 102, 103, 104, 105],
			current_status="Lobby"
		)
		
		SessionPlayer.objects.create(session=self.session, player_id=1, name="Gracz 1", lives=3, points=0)
		SessionPlayer.objects.create(session=self.session, player_id=2, name="Gracz 2", lives=3, points=0)
		SessionPlayer.objects.create(session=self.session, player_id=3, name="Gracz 3", lives=3, points=0)

	def test_initial_state(self):
		"""Checks if game is correctly created in DB."""
		self.assertEqual(self.session.current_status, "Lobby")
		self.assertEqual(self.session.session_players.count(), 3)
		self.assertEqual(self.session.question_asked_count, 0)

	def test_start_game_assigns_first_player_and_question(self):
		"""Checks if game start assigns the first question."""
		self.session.fsm.start_game(starting_player_id=1)
		
		self.assertEqual(self.session.current_status, "Opening Answering")
		self.assertEqual(self.session.current_player_id, 1)
		self.assertEqual(self.session.current_question_id, 101) 
		self.assertEqual(self.session.question_asked_count, 1)

	def test_opening_phase_correct_answer_updates_db(self):
		"""Checks cycle: Correct answer -> Evaluation -> Nomination."""
		self.session.fsm.start_game(starting_player_id=1)
		
		self.session.fsm.answer_opening(answer="Paryż", is_correct=True)
		
		player_1 = self.session.session_players.get(player_id=1)
		
		self.assertEqual(self.session.current_status, "Opening Evaluation")
		self.assertEqual(player_1.points, 10)
		self.assertEqual(self.session.nominator_id, 1)
		
		self.session.fsm.evaluate_opening()
		self.assertEqual(self.session.current_status, "Player Nomination")

	def test_opening_phase_wrong_answer_deducts_life_in_db(self):
		"""Checks cycle: Error -> Lose life -> Next player."""
		self.session.fsm.start_game(starting_player_id=1)
		
		self.session.fsm.answer_opening(answer="Źle", is_correct=False)
		
		player_1 = self.session.session_players.get(player_id=1)
		
		self.assertEqual(self.session.current_status, "Opening Evaluation")
		self.assertEqual(player_1.lives, 2)
		self.assertIsNone(self.session.nominator_id)
		
		self.session.fsm.evaluate_opening()
		self.assertEqual(self.session.current_status, "Opening Answering")
		self.assertEqual(self.session.current_player_id, 2) 

	def test_edge_case_nominator_suicide(self):
			"""Checks if next player becomes nominator after current dies."""
			self.session.fsm.start_game(starting_player_id=1)
			self.session.fsm.answer_opening(answer="Dobra odpowiedź", is_correct=True)
			self.session.fsm.evaluate_opening()
			self.session.save()
			
			player_1 = self.session.session_players.get(player_id=1)
			player_1.lives = 1
			player_1.save()
			
			self.session.fsm.nominate_player(target_player_id=1)
			self.session.save()
			
			self.session.fsm.answer_nominated(answer="Błąd", is_correct=False)
			
			self.session.save()
			self.session.refresh_from_db()
			
			self.assertEqual(self.session.current_status, "Nomination Evaluation")
			self.assertFalse(self.session.fsm.is_nominator_alive())
			
			self.session.fsm.evaluate_nomination()
			
			self.session.save()
			self.session.refresh_from_db()
			
			self.assertEqual(self.session.current_status, "Player Nomination")
			self.assertEqual(self.session.nominator_id, 2)
			self.assertEqual(self.session.current_player_id, 2)