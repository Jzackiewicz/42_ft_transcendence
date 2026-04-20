from django.test import TestCase
from game.models import GameSession, SessionPlayer, Question, SessionQuestion


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

	def test_start_game_sets_initial_state(self):
		self.fsm.start_game(starting_player_id=self.p1.id)
		self.session.save()
		self.session.refresh_from_db()

		self.assertEqual(self.session.current_player, self.p1)
		self.assertIsNotNone(self.session.current_question)

	def test_correct_answer_sets_last_correct_player_and_enters_nomination(self):
		self.fsm.start_game(starting_player_id=self.p1.id)
		self.session.save()

		self.fsm.submit_answer(answer="A", is_timeout=False)
		self.session.save()

		self.fsm.mark_correct()
		self.session.save()
		self.session.refresh_from_db()
		self.p1.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)
		self.assertEqual(self.session.last_correct_player, self.p1)
		self.assertEqual(self.p1.points, 10)

	def test_wrong_answer_without_last_correct_player_falls_back_to_next_alive_player(self):
		self.fsm.start_game(starting_player_id=self.p1.id)
		self.session.save()

		self.fsm.submit_answer(answer="wrong", is_timeout=False)
		self.session.save()

		self.fsm.mark_wrong()
		self.session.save()
		self.session.refresh_from_db()
		self.p1.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.ANSWERING)
		self.assertEqual(self.session.current_player, self.p2)
		self.assertEqual(self.p1.lives, 2)
		self.assertIsNotNone(self.session.current_question)

	def test_self_nomination_and_correct_answer_gives_twenty_bonus(self):
		self.fsm.start_game(starting_player_id=self.p1.id)
		self.session.save()

		self.fsm.submit_answer(answer="A", is_timeout=False)
		self.session.save()

		self.fsm.mark_correct()
		self.session.save()

		self.fsm.nominate_player(target_player_id=self.p1.id)
		self.session.save()
		self.session.refresh_from_db()

		self.assertEqual(self.session.current_player, self.p1)
		self.assertEqual(self.session.last_nominated_player, self.p1)

		self.fsm.submit_answer(answer="A again", is_timeout=False)
		self.session.save()

		self.fsm.mark_correct()
		self.session.save()
		self.p1.refresh_from_db()
		self.session.refresh_from_db()

		self.assertEqual(self.p1.points, 30)  # 10 + 20
		self.assertEqual(self.session.last_correct_player, self.p1)
		self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)

	def test_wrong_answer_with_alive_last_correct_player_returns_to_nomination(self):
		self.fsm.start_game(starting_player_id=self.p1.id)
		self.session.save()

		self.fsm.submit_answer(answer="A", is_timeout=False)
		self.session.save()

		self.fsm.mark_correct()
		self.session.save()

		self.fsm.nominate_player(target_player_id=self.p2.id)
		self.session.save()

		self.fsm.submit_answer(answer="wrong", is_timeout=False)
		self.session.save()

		self.fsm.mark_wrong()
		self.session.save()
		self.session.refresh_from_db()
		self.p2.refresh_from_db()

		self.assertEqual(self.session.current_status, GameSession.Status.NOMINATION)
		self.assertEqual(self.session.last_correct_player, self.p1)
		self.assertEqual(self.p2.lives, 2)

	def test_wrong_answer_on_last_life_ends_game(self):
		self.p1.lives = 1
		self.p1.save()
		
		self.p2.lives = 0
		self.p2.save()
		
		self.p3.lives = 3
		self.p3.save()

		self.fsm.start_game(starting_player_id=self.p1.id)
		self.session.save()

		self.fsm.submit_answer(answer="wrong", is_timeout=False)
		self.session.save()

		self.fsm.mark_wrong()
		self.session.save()
		self.session.refresh_from_db()
		self.p1.refresh_from_db()

		self.assertEqual(self.p1.lives, 0)
		self.assertEqual(self.session.current_status, GameSession.Status.GAME_OVER)

	def test_timeout_is_treated_like_wrong_answer(self):
		self.fsm.start_game(starting_player_id=self.p1.id)
		self.session.save()

		self.fsm.submit_answer(answer=None, is_timeout=True)
		self.session.save()

		self.fsm.mark_wrong()
		self.session.save()
		self.session.refresh_from_db()
		self.p1.refresh_from_db()

		self.assertEqual(self.p1.lives, 2)
		self.assertEqual(self.session.current_player, self.p2)