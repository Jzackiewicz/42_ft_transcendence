from game.models import GameSession, SessionPlayer
from .game_service import GameService
from django.db import transaction
from dataclasses import dataclass, field
from typing import Any

class GameAction:
	START_GAME = "start_game"
	SUBMIT_ANSWER = "submit_answer"
	NOMINATE_PLAYER = "nominate_player"
	EVALUATE_ANSWER = "evaluate_answer"
	END_GAME = "end_game"


@dataclass(frozen=True)
class GameActionRequest:
	session_id: int
	action: str
	actor_id: int | None = None
	payload: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class GameActionResult:
	session_id: int
	status: str
	action: str

class GameActionHandler:
	@transaction.atomic
	def handle_action(self, request):
		session = self._get_session(session_id=request.session_id)
		actor = self._get_actor(session=session, actor_id=request.actor_id)

		service = GameService(session)
		if request.action == GameAction.START_GAME:
			service.start_game_session()

		elif request.action == GameAction.SUBMIT_ANSWER:
			if actor is None:
				raise ValueError("Actor is required to submit answer")

			service.submit_player_answer(
				actor=actor,
				answer=request.payload.get("answer"),
			)

		elif request.action == GameAction.NOMINATE_PLAYER:
			if actor is None:
				raise ValueError("Actor is required to nominate player")

			target_player_id = request.payload.get("target_player_id")
			if target_player_id is None:
				raise ValueError("target_player_id is required")

			service.nominate_player(
				actor=actor,
				target_player_id=target_player_id,
			)

		elif request.action == GameAction.EVALUATE_ANSWER:
			service.evaluate_player_answer()

		# TODO: allow host of the game to end the game prematurely
		# elif request.action == GameAction.END_GAME:
		#     service.end_game_session()

		else:
			raise ValueError(f"Unsupported game action: {request.action}")

		session.refresh_from_db()

		return GameActionResult(
			session_id=session.id,
			status=session.current_status,
			action=request.action,
		)
	
	@staticmethod
	def _get_session(*, session_id: int) -> GameSession:
		if session_id is None:
			raise ValueError("session_id is required")
		return GameSession.objects.get(id=session_id)

	@staticmethod
	def _get_actor(*, session: GameSession, actor_id: int | None) -> SessionPlayer | None:
		if actor_id is None:
			return None

		return session.session_players.get(id=actor_id)