from django.core.exceptions import ValidationError
from django.db.models import Q
from game.models import GameSession, SessionPlayer

def _has_active_session(user, exclude_session_id: int | None = None) -> bool:
	if not user.is_authenticated:
		return False
			
	qs = SessionPlayer.objects.filter(user=user).exclude(
		session__current_status=GameSession.Status.GAME_OVER
	)
	if exclude_session_id is not None:
		qs = qs.exclude(session_id=exclude_session_id)
		
	active_condition = Q(disconnected_at__isnull=True) | Q(
		disconnected_at__isnull=False,
		lives__gt=0
	)
	return qs.filter(active_condition).exists()

def check_can_create_room(*, user) -> None:
	if not user.is_authenticated:
		raise ValidationError("User must be authenticated to create a room.")
	if _has_active_session(user):
		raise ValidationError("Cannot create a new room while active in another game.")

def check_can_join_room(*, session: GameSession, user) -> None:
	if not user.is_authenticated:
		raise ValidationError("User must be authenticated to join a room.")
	if not session:
		raise Exception("Room not found")
	if _has_active_session(user, exclude_session_id=session.id):
		raise ValidationError("Cannot join another room while active in a game.")
	if session.current_status != GameSession.Status.LOBBY:
		raise ValidationError("Cannot join a game that has already started or ended.")
	if session.session_players.count() >= session.max_players:
		raise ValidationError("Room is already full.")

def check_can_destroy_room(*, session: GameSession, user) -> None:
	if not session:
		raise Exception("Room not found")
	if session.host_player and session.host_player.user != user:
		raise ValidationError("Only the host can destroy the room.")
	if session.current_status != GameSession.Status.LOBBY:
		raise ValidationError("Cannot destroy a game that is already in progress.")