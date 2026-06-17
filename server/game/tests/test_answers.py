from django.test import TestCase
from game.models import GameSession, SessionPlayer, Question, SessionQuestion, AnswerAttempt
from game.services.game_flow.answers import normalize_string, check_answer_correctness


class AnswerNormalizationTests(TestCase):
	def test_empty_string(self):
		self.assertEqual(normalize_string(""), "")
		self.assertEqual(normalize_string(None), "")

	def test_basic_normalization(self):
		self.assertEqual(normalize_string("  WARSAW  "), "warsaw")
		self.assertEqual(normalize_string("United Kingdom"), "united kingdom")

	def test_punctuation_removal(self):
		self.assertEqual(normalize_string("h2o!"), "h2o")
		self.assertEqual(normalize_string("paris, france..."), "paris france")
		self.assertEqual(normalize_string("what? is - 'this'"), "what is this")

	def test_diacritics_and_polish_chars(self):
		# Polish characters mapping
		self.assertEqual(normalize_string("Kraków"), "krakow")
		self.assertEqual(normalize_string("Łódź"), "lodz")
		self.assertEqual(normalize_string("Gdańsk"), "gdansk")
		self.assertEqual(normalize_string("Świętokrzyskie"), "swietokrzyskie")
		self.assertEqual(normalize_string("Żółć"), "zolc")
		# Other common accents NFKD decomposition
		self.assertEqual(normalize_string("München"), "munchen")
		self.assertEqual(normalize_string("São Paulo"), "sao paulo")
		self.assertEqual(normalize_string("Montréal"), "montreal")


class AnswerCorrectnessTests(TestCase):
	def setUp(self):
		self.session = GameSession.objects.create()
		self.player = SessionPlayer.objects.create(
			session=self.session,
			display_name="Test Player",
			seat_number=1,
			lives=3,
		)

	def _create_attempt(self, correct_answer, player_answer, is_timeout=False):
		question = Question.objects.create(
			question_text="Dummy Question",
			correct_answer=correct_answer
		)
		session_question = SessionQuestion.objects.create(
			session=self.session,
			question=question,
			order_index=self.session.session_questions.count()
		)
		return AnswerAttempt.objects.create(
			session=self.session,
			session_question=session_question,
			player=self.player,
			answer_text=player_answer,
			is_timeout=is_timeout,
			answer_time_ms=1000
		)

	def test_timeout_always_fails(self):
		attempt = self._create_attempt(correct_answer="Paris", player_answer="Paris", is_timeout=True)
		self.assertFalse(check_answer_correctness(attempt))

	def test_strict_matching(self):
		# Correct: "Warsaw"
		attempt = self._create_attempt(correct_answer="Warsaw", player_answer="warsaw")
		self.assertTrue(check_answer_correctness(attempt))

		# Case-insensitivity and spacing normalized
		attempt = self._create_attempt(correct_answer="  Warsaw  ", player_answer="warsaw")
		self.assertTrue(check_answer_correctness(attempt))

		# Typo should fail under strict matching
		attempt = self._create_attempt(correct_answer="Warsaw", player_answer="wasraw")
		self.assertFalse(check_answer_correctness(attempt))

		# Roman numerals must match exactly
		attempt = self._create_attempt(correct_answer="Elizabeth II", player_answer="Elizabeth II")
		self.assertTrue(check_answer_correctness(attempt))

		attempt = self._create_attempt(correct_answer="Elizabeth II", player_answer="Elizabeth 2")
		self.assertFalse(check_answer_correctness(attempt))

	def test_alternative_answers(self):
		# Alternatives: "Dolly | Dolly the sheep | Sheep Dolly"
		# Dolly (passes)
		attempt = self._create_attempt(correct_answer="Dolly | Dolly the sheep | Sheep Dolly", player_answer="Dolly")
		self.assertTrue(check_answer_correctness(attempt))

		# Dolly the sheep (passes)
		attempt = self._create_attempt(correct_answer="Dolly | Dolly the sheep | Sheep Dolly", player_answer="Dolly the sheep")
		self.assertTrue(check_answer_correctness(attempt))

		# Sheep Dolly (passes)
		attempt = self._create_attempt(correct_answer="Dolly | Dolly the sheep | Sheep Dolly", player_answer="Sheep Dolly")
		self.assertTrue(check_answer_correctness(attempt))

		# Dolly the ship (fails due to strict matching)
		attempt = self._create_attempt(correct_answer="Dolly | Dolly the sheep | Sheep Dolly", player_answer="Dolly the ship")
		self.assertFalse(check_answer_correctness(attempt))
