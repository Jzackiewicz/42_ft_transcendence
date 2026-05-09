from game.models import GameSession
from game.serializers import GameStateSnapshotSerializer

def get_game_snapshot(session_id: int) -> dict:
	session = GameSession.objects.prefetch_related(
		'session_players', 'current_question__question'
	).get(id=session_id)
	return GameStateSnapshotSerializer(session).data