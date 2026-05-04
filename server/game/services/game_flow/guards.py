from game.models import GameSession, SessionPlayer, AnswerAttempt


def require_status(session: GameSession, expected_status: str) -> None:
	if session.current_status != expected_status:
		raise ValueError(f"Game session is not in {expected_status} state")


def require_current_player(session: GameSession) -> None:
	if session.current_player is None:
		raise ValueError("Game session has no current player")


def require_current_question(session: GameSession) -> None:
	if session.current_question is None:
		raise ValueError("Game session has no current question")


def require_current_attempt(session: GameSession) -> None:
	if session.current_attempt is None:
		raise ValueError("Game session has no current attempt")


def require_no_current_attempt(session: GameSession) -> None:
	if session.current_attempt is not None:
		raise ValueError("Game session already has a current attempt")


def require_actor_is_current_player(session: GameSession, actor: SessionPlayer, action: str) -> None:
	if actor is None or actor.id != session.current_player_id:
		raise ValueError(f"Only current player can {action}")


def require_actor_is_last_correct_player(session: GameSession, actor: SessionPlayer, action: str) -> None:
	if actor is None or actor.id != session.last_correct_player_id:
		raise ValueError(f"Only last correct player can {action}")


def get_pending_current_attempt(session: GameSession) -> AnswerAttempt:
	require_current_attempt(session)

	attempt = session.current_attempt

	if attempt.session_id != session.id:
		raise ValueError("Current attempt does not belong to this session")

	if attempt.evaluation_status != AnswerAttempt.EvaluationStatus.PENDING:
		raise ValueError("Current attempt is not pending")

	if attempt.started_at is None:
		raise ValueError("Current attempt has no started_at timestamp")

	return attempt