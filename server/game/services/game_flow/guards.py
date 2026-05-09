from django.core.exceptions import ValidationError
from game.models import GameSession, SessionPlayer, AnswerAttempt, Question


def require_status(session: GameSession, expected_status: str) -> None:
	if session.current_status != expected_status:
		raise ValidationError(f"Game session is not in {expected_status} state")


def require_minimum_players(session: GameSession) -> None:
	if session.session_players.count() < 2:
		raise ValidationError("Cannot start game with fewer than 2 players")


def require_questions_exist(session: GameSession) -> None:
	if not session.session_questions.exists():
		raise ValidationError("Cannot start game without questions")


def require_enough_questions_in_db(amount: int) -> None:
	available = Question.objects.count()
	if available == 0:
		raise ValidationError("Cannot start game without questions in the database.")
	if available < amount:
		raise ValidationError(f"Not enough questions. Required: {amount}, available: {available}.")


def require_starting_player(player: SessionPlayer | None) -> None:
	if player is None:
		raise ValidationError("No alive players to start the game")


def require_player_alive(player: SessionPlayer, action: str) -> None:
	if player.lives <= 0:
		raise ValidationError(f"Cannot {action} a dead player")


def require_current_player(session: GameSession) -> None:
	if session.current_player is None:
		raise ValidationError("Game session has no current player")


def require_current_question(session: GameSession) -> None:
	if session.current_question is None:
		raise ValidationError("Game session has no current question")


def require_current_attempt(session: GameSession) -> None:
	if session.current_attempt is None:
		raise ValidationError("Game session has no current attempt")


def require_no_current_attempt(session: GameSession) -> None:
	if session.current_attempt is not None:
		raise ValidationError("Game session already has a current attempt")


def require_actor_is_current_player(session: GameSession, actor: SessionPlayer | None, action: str) -> None:
	require_action_actor(actor, action)
	if actor.id != session.current_player_id:
		raise ValidationError(f"Only current player can {action}")


def require_actor_is_last_correct_player(session: GameSession, actor: SessionPlayer | None, action: str) -> None:
	require_action_actor(actor, action)
	if actor.id != session.last_correct_player_id:
		raise ValidationError(f"Only last correct player can {action}")


def get_pending_current_attempt(session: GameSession) -> AnswerAttempt:
	require_current_attempt(session)

	attempt = session.current_attempt

	if attempt.session_id != session.id:
		raise ValidationError("Current attempt does not belong to this session")

	if attempt.evaluation_status != AnswerAttempt.EvaluationStatus.PENDING:
		raise ValidationError("Current attempt is not pending")

	if attempt.started_at is None:
		raise ValidationError("Current attempt has no started_at timestamp")

	return attempt


def require_attempt_correctness_determined(attempt: AnswerAttempt) -> None:
	if attempt.is_correct is None:
		raise ValidationError("Attempt correctness not determined")


def require_action_actor(actor: SessionPlayer | None, action: str) -> None:
	if actor is None:
		raise ValidationError(f"Actor is required to {action}")


def require_target_player_id(target_player_id: int | None) -> None:
	if target_player_id is None:
		raise ValidationError("target_player_id is required")


def require_session_id(session_id: int | None) -> None:
	if session_id is None:
		raise ValidationError("session_id is required")
