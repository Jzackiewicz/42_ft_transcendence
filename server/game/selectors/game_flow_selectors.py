from datetime import timedelta

from game.models import GameSession
from game.serializers import GameStateSnapshotSerializer

def _get_deadlines_data(session: GameSession) -> dict:
	data = {
		'current_attempt_started_at': None,
		'turn_deadline_at': None,
		'nomination_deadline_at': None,
	}

	if session.current_attempt and session.current_attempt.started_at:
		started_at = session.current_attempt.started_at
		deadline_at = started_at + timedelta(
			milliseconds=session.answer_time_limit_ms
		)
		data['current_attempt_started_at'] = started_at.isoformat()
		data['turn_deadline_at'] = deadline_at.isoformat()

	if session.current_status == GameSession.Status.NOMINATION and session.nomination_started_at:
		nomination_deadline = session.nomination_started_at + timedelta(
			milliseconds=session.nomination_time_limit_ms
		)
		data['nomination_deadline_at'] = nomination_deadline.isoformat()

	return data


def get_game_snapshot(session_id: int) -> dict:
	session = GameSession.objects.select_related(
		'current_attempt', 'current_question__question'
	).prefetch_related(
		'session_players__user__profile'
	).get(id=session_id)
	
	snapshot = dict(GameStateSnapshotSerializer(session).data)
	snapshot.update(_get_deadlines_data(session))

	return snapshot

