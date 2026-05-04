from game.models import GameSession, AnswerAttempt
from django.utils import timezone


def set_end_game_stats(session: GameSession) -> None:
	alive_players = list(session.session_players.filter(lives__gt=0))
	if len(alive_players) == 1:
		session.winner = alive_players[0]
		session.end_reason = GameSession.EndReason.LAST_PLAYER_ALIVE
	else:
		session.winner = (
			session.session_players.order_by(
				"-points", "-answered_count", 
				"total_answer_time_ms", "seat_number")
				.first()
		)
		session.end_reason = GameSession.EndReason.QUESTIONS_EXHAUSTED
	session.ended_at = timezone.now()
	session.current_question = None
	session.current_attempt = None
	session.save()

def create_answer_attempt(session: GameSession) -> AnswerAttempt:
	return AnswerAttempt.objects.create(
			session=session,
			player=session.current_player,
			session_question=session.current_question,
			answer_text=None,
			is_timeout=False,
			is_correct=None,
			evaluation_status=AnswerAttempt.EvaluationStatus.PENDING,
			answer_time_ms=0,
			started_at=timezone.now(),
		)


def submit_answer_attempt(session: GameSession, attempt: AnswerAttempt, answer_text: str | None) -> None:
	elapsed = timezone.now() - attempt.started_at
	answer_time_ms = max(int(elapsed.total_seconds() * 1000), 0)
	is_timeout = answer_time_ms >= session.answer_time_limit_ms

	attempt.answer_time_ms = answer_time_ms
	attempt.is_timeout = is_timeout
	if is_timeout:
		attempt.answer_text = None
	else:
		attempt.answer_text = answer_text
	attempt.save()


def assign_next_question(session: GameSession) -> None:
	next_question = session.session_questions.filter(
		order_index=session.question_asked_count
	).first()

	if next_question is not None:
		session.current_question = next_question
		session.question_asked_count += 1
	else:
		session.current_question = None