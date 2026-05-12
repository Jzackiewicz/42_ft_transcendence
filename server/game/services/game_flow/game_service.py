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
	require_actor_is_host,
	require_minimum_players,
	require_questions_exist,
	require_starting_player,
	require_player_alive,
	require_action_actor,
	require_target_player_id,
	require_player_in_session,
)

from .lifecycle import (
	set_end_game_stats,
	create_answer_attempt,
	submit_answer_attempt,
	assign_next_question,
	cancel_game,
	handle_disconnect_in_lobby,
	handle_disconnect_in_answering,
	handle_disconnect_in_nomination,
	handle_evaluate_timeout,
	assign_random_questions_to_session
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
			require_status(self.session, GameSession.Status.GAME_OVER)
			set_end_game_stats(self.session)
			return

		if should_fallback:
			self._no_last_correct_player_fallback()
			self.session.save()
			self._start_answering_turn()

	def _handle_active_game_disconnect(self, actor: SessionPlayer) -> None:
		if self.session.current_status == GameSession.Status.ANSWERING:
			handle_disconnect_in_answering(self.session, actor)

		actor.lives = 0
		actor.save(update_fields=['lives'])

		if self.session.is_game_over():
			cancel_game(self.session)
			return

		if self.session.current_status == GameSession.Status.EVALUATION:
			apply_answer_verdict(self.session)
			self._advance_after_evaluation()
		elif self.session.current_status == GameSession.Status.NOMINATION:
			if handle_disconnect_in_nomination(self.session, actor):
				self._start_answering_turn()

	def start_game_session(self, actor: SessionPlayer | None):
		require_status(self.session, GameSession.Status.LOBBY)
		require_actor_is_host(self.session, actor, "start the game")
		require_minimum_players(self.session)
		
		assign_random_questions_to_session(self.session, amount=10)
		require_questions_exist(self.session)
		
		starting_player = get_random_alive_player(self.session)
		require_starting_player(starting_player)

		self.session.current_player = starting_player
		self.session.last_correct_player = None
		self.session.last_nominated_player = None

		self.session.fsm.start_game()
		self.session.started_at = timezone.now()
		self.session.save()
		self._start_answering_turn()

	def nominate_player(self, actor: SessionPlayer | None, target_player_id: int | None) -> None:
		require_status(self.session, GameSession.Status.NOMINATION)
		require_actor_is_last_correct_player(self.session, actor, "nominate")
		require_target_player_id(target_player_id)

		target = self.session.session_players.filter(id=target_player_id).first()
		require_player_in_session(target, self.session)
		require_player_alive(target, "nominate")

		self.session.last_nominated_player = target
		self.session.current_player = target

		self.session.fsm.nominate_player()
		self.session.save()
		self._start_answering_turn()

	def submit_player_answer(self, actor: SessionPlayer | None, answer: str | None) -> None:
		require_status(self.session, GameSession.Status.ANSWERING)
		require_actor_is_current_player(self.session, actor, "submit answer")
		require_current_player(self.session)
		require_current_question(self.session)

		attempt = get_pending_current_attempt(self.session)
		submit_answer_attempt(self.session, attempt, answer)

		self.session.fsm.submit_answer()
		self.session.save()
		self.evaluate_answer()

	def evaluate_timeout(self) -> None:
		require_status(self.session, GameSession.Status.ANSWERING)
		attempt = get_pending_current_attempt(self.session)
		handle_evaluate_timeout(self.session, attempt)
		self.session.fsm.submit_answer()
		self.session.save()
		self.evaluate_answer()

	def evaluate_answer(self) -> None:
		require_status(self.session, GameSession.Status.EVALUATION)
		evaluate_current_attempt(self.session)
		apply_answer_verdict(self.session)
		self._advance_after_evaluation()

	def	disconnect_player(self, actor: SessionPlayer | None) -> None:
		require_action_actor(actor, "disconnect")
		
		if self.session.current_status == GameSession.Status.LOBBY:
			handle_disconnect_in_lobby(self.session, actor)
		elif self.session.current_status == GameSession.Status.GAME_OVER:
			return
		else:
			self._handle_active_game_disconnect(actor)