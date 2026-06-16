from datetime import timedelta

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
	DISCONNECT = "disconnect"
	LEAVE_GAME = "leave_game"


@dataclass(frozen=True)
class GameActionRequest:
	session_id: int
	action: str
	user: Any | None = None
	payload: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class GameActionResult:
	session_id: int
	status: str | None
	action: str
	session_deleted: bool = False
	timer_data: dict | None = None

class GameActionHandler:
	@transaction.atomic
	def handle_action(self, request):
		session = self._get_session(session_id=request.session_id)
		actor = self._get_actor(session=session, user=request.user)

		service = GameService(session)
		if request.action == GameAction.START_GAME:
			service.start_game_session(actor=actor)

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

		elif request.action == GameAction.DISCONNECT:
			service.disconnect_player(actor=actor)

		elif request.action == GameAction.LEAVE_GAME:
			service.leave_game(actor=actor)

		else:
			raise ValidationError(f"Unsupported game action: {request.action}")

		is_deleted = not bool(session.pk)

		if not is_deleted:
			session.refresh_from_db()

		return GameActionResult(
			session_id=request.session_id,
			status=None if is_deleted else session.current_status,
			action=request.action,
			session_deleted=is_deleted,
			timer_data=None if is_deleted else self._build_timer_data(session),
		)
	
	@transaction.atomic
	def handle_timer_timeout(self, session_id: int, action: str) -> GameActionResult:
		session = self._get_session(session_id=session_id)
		service = GameService(session)

		if action == "evaluate_timeout":
			service.evaluate_timeout()
		elif action == "handle_evaluation_finish":
			service.resolve_evaluation()
		elif action == "nomination_timeout":
			service.nominate_timeout()
		else:
			raise ValidationError(f"Unsupported timer action: {action}")

		session.refresh_from_db()
		return GameActionResult(
			session_id=session.id,
			status=session.current_status,
			action=action,
			timer_data=self._build_timer_data(session),
		)

	@transaction.atomic
	def sync_game_disconnections(self, session_id: int) -> GameActionResult:
		session = GameSession.objects.filter(id=session_id).select_for_update().first()
		if not session:
			return GameActionResult(
				session_id=session_id,
				status=None,
				action="sync_disconnections",
				session_deleted=True,
			)

		GameService(session).expire_disconnected_players()

		# Check if the session was deleted during player expiration
		is_deleted = not GameSession.objects.filter(id=session_id).exists()
		if is_deleted:
			return GameActionResult(
				session_id=session_id,
				status=None,
				action="sync_disconnections",
				session_deleted=True,
			)

		session.refresh_from_db()
		return GameActionResult(
			session_id=session_id,
			status=session.current_status,
			action="sync_disconnections",
			timer_data=self._build_timer_data(session),
		)

	@staticmethod
	def _build_timer_data(session: GameSession) -> dict | None:
		attempt = session.current_attempt

		if session.current_status == GameSession.Status.ANSWERING and attempt and attempt.started_at:
			start_time = attempt.started_at
			limit_ms = session.answer_time_limit_ms
			timer_type = 'answer_timeout'
		elif session.current_status == GameSession.Status.EVALUATION and attempt and attempt.evaluated_at:
			start_time = attempt.evaluated_at
			limit_ms = session.evaluation_time_limit_ms
			timer_type = 'evaluation_finish'
		elif session.current_status == GameSession.Status.NOMINATION and session.nomination_started_at:
			start_time = session.nomination_started_at
			limit_ms = session.nomination_time_limit_ms
			timer_type = 'nomination_timeout'
		else:
			return None

		return {
			'type': timer_type,
			'deadline_at': start_time + timedelta(milliseconds=limit_ms),
		}

	@staticmethod
	def _get_session(*, session_id: int) -> GameSession:
		require_session_id(session_id)
		return GameSession.objects.select_for_update().get(id=session_id)

	@staticmethod
	def _get_actor(*, session: GameSession, user) -> SessionPlayer | None:
		if user is None or not user.is_authenticated:
			return None

		return session.session_players.filter(user=user).first()