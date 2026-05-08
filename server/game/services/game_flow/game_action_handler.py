from game.models import GameSession, SessionPlayer
from .game_service import GameService
from django.db import transaction
from django.core.exceptions import ValidationError
from dataclasses import dataclass, field
from typing import Any
from .guards import (
	require_session_id,
)

class GameAction:
	START_GAME = "start_game"
	SUBMIT_ANSWER = "submit_answer"
	NOMINATE_PLAYER = "nominate_player"
	EVALUATE_ANSWER = "evaluate_answer"
	DISCONNECT = "disconnect"


@dataclass(frozen=True)
class GameActionRequest:
	session_id: int
	action: str
	user: Any | None = None
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
		actor = self._get_actor(session=session, user=request.user)

		service = GameService(session)
		if request.action == GameAction.START_GAME:
			service.start_game_session()

		elif request.action == GameAction.SUBMIT_ANSWER:
			service.submit_player_answer(
				actor=actor,
				answer=request.payload.get("answer"),
			)

		elif request.action == GameAction.NOMINATE_PLAYER:
			service.nominate_player(
				actor=actor,
				target_player_id=request.payload.get("target_player_id"),
			)

		elif request.action == GameAction.EVALUATE_ANSWER:
			service.evaluate_player_answer()

		elif request.action == GameAction.DISCONNECT:
			service.disconnect_player(actor=actor)

		else:
			raise ValidationError(f"Unsupported game action: {request.action}")

		session.refresh_from_db()

		return GameActionResult(
			session_id=session.id,
			status=session.current_status,
			action=request.action,
		)
	
	@staticmethod
	def _get_session(*, session_id: int) -> GameSession:
		require_session_id(session_id)
		return GameSession.objects.select_for_update().get(id=session_id)

	@staticmethod
	def _get_actor(*, session: GameSession, user) -> SessionPlayer | None:
		if user is None or not user.is_authenticated:
			return None

		return session.session_players.filter(user=user).first()