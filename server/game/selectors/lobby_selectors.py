from game.models import GameSession, SessionPlayer


def get_room_by_uuid(*, session_uuid: str):    
	return GameSession.objects.filter(session_uuid=session_uuid).first()

def verify_player_in_session(*, session_uuid: str, user) -> int | None:
	if not user.is_authenticated:
		return None
		
	session = GameSession.objects.filter(session_uuid=session_uuid).first()
	if not session:
		return None

	if not SessionPlayer.objects.filter(session=session, user=user).exists():
		return None

	return session.id