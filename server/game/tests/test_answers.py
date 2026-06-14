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

	def test_short_answers_must_match_exactly(self):
		# Short (len <= 3) correct answer: "4"
		attempt = self._create_attempt(correct_answer="4", player_answer="4")
		self.assertTrue(check_answer_correctness(attempt))

		attempt = self._create_attempt(correct_answer="4", player_answer="5")
		self.assertFalse(check_answer_correctness(attempt))

		# Short (len <= 3) correct answer: "yes"
		attempt = self._create_attempt(correct_answer="yes", player_answer="yes")
		self.assertTrue(check_answer_correctness(attempt))

		attempt = self._create_attempt(correct_answer="yes", player_answer="ye")
		self.assertFalse(check_answer_correctness(attempt))

	def test_medium_answers_similarity_threshold(self):
		# Medium (4 <= len <= 6) correct answer: "Paris" (len = 5)
		# Exact match
		attempt = self._create_attempt(correct_answer="Paris", player_answer="paris")
		self.assertTrue(check_answer_correctness(attempt))

		# 1 character typo: "pari" (len 4), ratio = 2*4/9 = 0.888 >= 0.85 (Passes)
		attempt = self._create_attempt(correct_answer="Paris", player_answer="pari")
		self.assertTrue(check_answer_correctness(attempt))

		# 1 extra char typo: "pariss" (len 6), ratio = 2*5/11 = 0.909 >= 0.85 (Passes)
		attempt = self._create_attempt(correct_answer="Paris", player_answer="pariss")
		self.assertTrue(check_answer_correctness(attempt))

		# Too many typos: "parks" (len 5), ratio = 2*3/10 = 0.60 < 0.85 (Fails)
		attempt = self._create_attempt(correct_answer="Paris", player_answer="parks")
		self.assertFalse(check_answer_correctness(attempt))

	def test_long_answers_similarity_threshold(self):
		# Long (len > 6) correct answer: "Washington" (len = 10)
		# Exact match after normalization
		attempt = self._create_attempt(correct_answer="Washington", player_answer="  washington  ")
		self.assertTrue(check_answer_correctness(attempt))

		# Typo: "wahsington" (ratio = 2*9/20 = 0.90 >= 0.80) -> Passes
		attempt = self._create_attempt(correct_answer="Washington", player_answer="wahsington")
		self.assertTrue(check_answer_correctness(attempt))

		# Typo: "washinton" (ratio = 2*9/19 = 0.947 >= 0.80) -> Passes
		attempt = self._create_attempt(correct_answer="Washington", player_answer="washinton")
		self.assertTrue(check_answer_correctness(attempt))

		# Too many differences: "washingmaching" (ratio = 2*7/24 = 0.583 < 0.80) -> Fails
		attempt = self._create_attempt(correct_answer="Washington", player_answer="washingmaching")
		self.assertFalse(check_answer_correctness(attempt))
