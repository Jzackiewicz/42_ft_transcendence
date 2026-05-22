from game.models import GameSession, SessionPlayer


def get_room_by_uuid(*, session_uuid: str):    
	return GameSession.objects.filter(session_uuid=session_uuid).first()

def verify_player_in_session(*, session_uuid: str, user) -> tuple[int, int] | tuple[None, None]:
	if not user.is_authenticated:
		return None, None
		
	session = GameSession.objects.filter(session_uuid=session_uuid).first()
	if not session:
		return None, None

	player = SessionPlayer.objects.filter(session=session, user=user).first()
	if not player:
		return None, None
	
	return session.id, player.id