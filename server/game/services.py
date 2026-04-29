from .models import GameSession, SessionPlayer, AnswerAttempt
from django.utils import timezone

class GameService:
	def __init__(self, session: GameSession):
		self.session = session

	def _assign_next_question(self) -> None:
		next_question = self.session.session_questions.filter(
			order_index=self.session.question_asked_count
		).first()

		if next_question is not None:
			self.session.current_question = next_question
			self.session.question_asked_count += 1
		else:
			self.session.current_question = None

	def _get_random_player(self) -> SessionPlayer | None:
		return self.session.session_players.filter(lives__gt=0).order_by("?").first()

	def _get_next_alive_player(self, current_player: SessionPlayer) -> SessionPlayer:
		alive_players = list(
			self.session.session_players.filter(lives__gt=0).order_by("seat_number")
		)

		if not alive_players:
			return current_player

		for player in alive_players:
			if player.seat_number > current_player.seat_number:
				return player
		return alive_players[0]

	def _no_last_correct_player_fallback(self) -> None:
		next_player = self._get_next_alive_player(self.session.current_player)
		self.session.current_player = next_player

	def _check_answer_correctness(self, attempt: AnswerAttempt) -> bool:
		'''
			Temporary function to check answer correctness.
			In the future, this should be replaced with a more complex evaluation logic.
		'''
		if attempt.is_timeout:
			return False
		
		question = attempt.session_question.question
		correct_answer = question.correct_answer.strip().lower()
		player_answer = (attempt.answer_text or "").strip().lower()

		return correct_answer == player_answer

	def _apply_correct_answer_effects(self, attempt: AnswerAttempt) -> None:
		player = attempt.player
		if self.session.last_nominated_player_id == player.id:
			player.points += 20
		else:
			player.points += 10
		player.answered_count += 1
		player.total_answer_time_ms += attempt.answer_time_ms
		player.save()
		self.session.last_correct_player = player
	
	def _apply_wrong_answer_effects(self, attempt: AnswerAttempt) -> None:
		player = attempt.player
		if player.lives > 0:
			player.lives -= 1
		player.answered_count += 1
		player.total_answer_time_ms += attempt.answer_time_ms
		player.save()

	def _advance_after_evaluation(self) -> None:
		should_fallback = (
			not self.session.is_game_over()
			and not self.session.has_last_correct_player_alive()
		)

		self.session.fsm.resolve_evaluation()
		self.session.save()
		
		if self.session.current_status == GameSession.Status.GAME_OVER:
			self.end_game_session()
			return

		if should_fallback:
			self._no_last_correct_player_fallback()
			self.session.save()
			self._start_answering_turn()

	def _apply_answer_verdict(self) -> None:
		attempt = self.session.current_attempt

		if attempt is None:
			raise ValueError("No attempt to apply verdict for")

		if attempt.is_correct is None:
			raise ValueError("Attempt correctness not determined")
		
		if attempt.is_correct:
			self._apply_correct_answer_effects(attempt)
		else:
			self._apply_wrong_answer_effects(attempt)

		self.session.current_attempt = None
		self.session.save()

		self._advance_after_evaluation()

	def _set_end_game_stats(self) -> None:
		alive_players = list(self.session.session_players.filter(lives__gt=0))
		if len(alive_players) == 1:
			self.session.winner = alive_players[0]
			self.session.end_reason = GameSession.EndReason.LAST_PLAYER_ALIVE
		else:
			self.session.winner = (
				self.session.session_players.order_by("-points", "-answered_count","total_answer_time_ms", "seat_number").first()
			)
			self.session.end_reason = GameSession.EndReason.QUESTIONS_EXHAUSTED
		self.session.ended_at = timezone.now()
		self.session.current_question = None
		self.session.current_attempt = None
		self.session.save()

	def start_game_session(self):
		if self.session.current_status != GameSession.Status.LOBBY:
			raise ValueError("Game session is not in lobby state")
		if self.session.session_players.count() < 2:
			raise ValueError("Cannot start game with fewer than 2 players")

		if not self.session.session_questions.exists():
			raise ValueError("Cannot start game without questions")
		starting_player = self._get_random_player()

		self.session.current_player = starting_player
		self.session.last_correct_player = None
		self.session.last_nominated_player = None

		self.session.fsm.start_game()
		self.session.started_at = timezone.now()
		self.session.save()
		self._start_answering_turn()

	def nominate_player(self, actor: SessionPlayer, target_player_id: int) -> None:
		if self.session.current_status != GameSession.Status.NOMINATION:
			raise ValueError("Game session is not in nomination state")
		if actor.id != self.session.last_correct_player_id:
			raise ValueError("Only last correct player can nominate")
		target = self.session.session_players.get(id=target_player_id)
		if target.lives <= 0:
			raise ValueError("Cannot nominate a dead player")

		self.session.last_nominated_player = target
		self.session.current_player = target

		self.session.fsm.nominate_player()
		self.session.save()
		self._start_answering_turn()

	def _start_answering_turn(self) -> None:
		if self.session.current_status != GameSession.Status.ANSWERING:
			raise ValueError("Game session is not in answering state")
		if self.session.current_player is None:
			raise ValueError("Cannot start answering turn without current player")
		if self.session.current_attempt is not None:
			raise ValueError("Cannot start answering turn with pending attempt")

		self._assign_next_question()

		if self.session.current_question is None:
			raise ValueError("Cannot start answering turn without current question")

		attempt = AnswerAttempt.objects.create(
			session=self.session,
			player=self.session.current_player,
			session_question=self.session.current_question,
			answer_text=None,
			is_timeout=False,
			is_correct=None,
			evaluation_status=AnswerAttempt.EvaluationStatus.PENDING,
			answer_time_ms=0,
			started_at=timezone.now(),
		)

		self.session.current_attempt = attempt
		self.session.save()

	def submit_player_answer(self, actor: SessionPlayer, answer: str | None) -> None:
		if self.session.current_status != GameSession.Status.ANSWERING:
			raise ValueError("Game session is not in answering state")
		if actor.id != self.session.current_player_id:
			raise ValueError("Only current player can submit answer")
		if self.session.current_attempt is None:
			raise ValueError("No active attempt to submit answer for")
		
		if self.session.current_player is None:
			raise ValueError("Cannot submit answer without current player")

		if self.session.current_question is None:
			raise ValueError("Cannot submit answer without current question")

		attempt = self.session.current_attempt
		
		if attempt.session_id != self.session.id:
			raise ValueError("Current attempt does not belong to this session")

		if attempt.evaluation_status != AnswerAttempt.EvaluationStatus.PENDING:
			raise ValueError("Current attempt is not pending")

		if attempt.started_at is None:
			raise ValueError("Current attempt has no started_at")

		elapsed = timezone.now() - attempt.started_at
		answer_time_ms = max(int(elapsed.total_seconds() * 1000), 0)
		is_timeout = answer_time_ms >= self.session.answer_time_limit_ms

		attempt.answer_time_ms = answer_time_ms
		attempt.is_timeout = is_timeout
		if is_timeout:
			attempt.answer_text = None
		else:
			attempt.answer_text = answer
		attempt.save()

		self.session.fsm.submit_answer()
		self.session.save()

	def evaluate_player_answer(self) -> None:
		if self.session.current_status != GameSession.Status.EVALUATION:
			raise ValueError("Game session is not in evaluation state")
		attempt = self.session.current_attempt
		if attempt is None:
			raise ValueError("No attempt to evaluate")
		
		attempt.is_correct = self._check_answer_correctness(attempt=attempt)
		attempt.evaluation_status = AnswerAttempt.EvaluationStatus.EVALUATED
		attempt.evaluated_at = timezone.now()
		attempt.save()
		self._apply_answer_verdict()

	def end_game_session(self):
		if self.session.current_status != GameSession.Status.GAME_OVER:
			raise ValueError("Game session is not in game over state")
		
		self._set_end_game_stats()