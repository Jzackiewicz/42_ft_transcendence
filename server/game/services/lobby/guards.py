from django.core.exceptions import ValidationError
from game.models import GameSession


def check_can_create_room(*, user) -> None:
	if not user.is_authenticated:
		raise ValidationError("User must be authenticated to create a room.")

def check_can_join_room(*, session: GameSession, user) -> None:
	if not user.is_authenticated:
		raise ValidationError("User must be authenticated to join a room.")
	if not session:
		raise Exception("Room not found")
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