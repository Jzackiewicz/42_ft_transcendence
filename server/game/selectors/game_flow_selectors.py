from datetime import timedelta

from game.models import GameSession
from game.serializers import GameStateSnapshotSerializer

def get_game_snapshot(session_id: int) -> dict:
	session = GameSession.objects.select_related(
		'current_attempt', 'current_question__question'
	).prefetch_related(
		'session_players'
	).get(id=session_id)
	snapshot = dict(GameStateSnapshotSerializer(session).data)

	if session.current_attempt and session.current_attempt.started_at:
		started_at = session.current_attempt.started_at
		deadline_at = started_at + timedelta(
			milliseconds=session.answer_time_limit_ms
		)
		snapshot['current_attempt_started_at'] = started_at.isoformat()
		snapshot['turn_deadline_at'] = deadline_at.isoformat()
	else:
		snapshot['current_attempt_started_at'] = None
		snapshot['turn_deadline_at'] = None

	return snapshot
