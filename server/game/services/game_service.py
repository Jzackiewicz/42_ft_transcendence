from django.utils import timezone

from game.models import GameSession, SessionPlayer

from .guards import (
    require_status,
    require_current_player,
    require_current_question,
    require_no_current_attempt,
    require_actor_is_current_player,
    require_actor_is_last_correct_player,
    get_pending_current_attempt,
)

from .lifecycle import (
	set_end_game_stats,
    create_answer_attempt,
    submit_answer_attempt,
    assign_next_question
)

from .answers import (
    apply_answer_verdict,
    evaluate_current_attempt
)

from .player_selection import (
    get_next_alive_player, 
    get_random_alive_player
)


class GameService:
	def __init__(self, session: GameSession):
		self.session = session

	def _no_last_correct_player_fallback(self) -> None:
		require_current_player(self.session)
		next_player = get_next_alive_player(
			self.session,
			self.session.current_player
		)
		self.session.current_player = next_player

	def _start_answering_turn(self) -> None:
		require_status(self.session, GameSession.Status.ANSWERING)
		require_current_player(self.session)
		require_no_current_attempt(self.session)

		assign_next_question(self.session)
		require_current_question(self.session)

		attempt = create_answer_attempt(self.session)

		self.session.current_attempt = attempt
		self.session.save()

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

	def start_game_session(self):
		require_status(self.session, GameSession.Status.LOBBY)
		if self.session.session_players.count() < 2:
			raise ValueError("Cannot start game with fewer than 2 players")
		if not self.session.session_questions.exists():
			raise ValueError("Cannot start game without questions")
		
		starting_player = get_random_alive_player(self.session)
		if starting_player is None:
			raise ValueError("No alive players to start the game")

		self.session.current_player = starting_player
		self.session.last_correct_player = None
		self.session.last_nominated_player = None

		self.session.fsm.start_game()
		self.session.started_at = timezone.now()
		self.session.save()
		self._start_answering_turn()

	def nominate_player(self, actor: SessionPlayer, target_player_id: int) -> None:
		require_status(self.session, GameSession.Status.NOMINATION)
		require_actor_is_last_correct_player(self.session, actor, "nominate")
		
		target = self.session.session_players.get(id=target_player_id)
		if target.lives <= 0:
			raise ValueError("Cannot nominate a dead player")

		self.session.last_nominated_player = target
		self.session.current_player = target

		self.session.fsm.nominate_player()
		self.session.save()
		self._start_answering_turn()

	def submit_player_answer(self, actor: SessionPlayer, answer: str | None) -> None:
		require_status(self.session, GameSession.Status.ANSWERING)
		require_actor_is_current_player(self.session, actor, "submit answer")
		require_current_player(self.session)
		require_current_question(self.session)

		attempt = get_pending_current_attempt(self.session)
		submit_answer_attempt(self.session, attempt, answer)

		self.session.fsm.submit_answer()
		self.session.save()


	def evaluate_player_answer(self) -> None:
		require_status(self.session, GameSession.Status.EVALUATION)
		evaluate_current_attempt(self.session)
		apply_answer_verdict(self.session)
		self._advance_after_evaluation()

	def end_game_session(self):
		require_status(self.session, GameSession.Status.GAME_OVER)
		set_end_game_stats(self.session)