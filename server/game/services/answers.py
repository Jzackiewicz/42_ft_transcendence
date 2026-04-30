from game.models import GameSession, SessionPlayer, AnswerAttempt
from django.utils import timezone


def check_answer_correctness(attempt: AnswerAttempt) -> bool:
	'''
		Temporary function to check answer correctness.
		In the future, this should be replaced with a more complex evaluation logic.
	'''
	if attempt.is_timeout:
		return False
	
	question = attempt.session_question.question
	correct_answer = question.correct_answer.strip().lower()
	player_answer = (attempt.answer_text or "").strip().lower()

	return correct_answer == player_answer

def apply_correct_answer_effects(session: GameSession,attempt: AnswerAttempt) -> None:
	player = attempt.player
	if session.last_nominated_player_id == player.id:
		player.points += 20
	else:
		player.points += 10
	player.answered_count += 1
	player.total_answer_time_ms += attempt.answer_time_ms
	player.save()
	session.last_correct_player = player

def apply_wrong_answer_effects(attempt: AnswerAttempt) -> None:
	player = attempt.player
	if player.lives > 0:
		player.lives -= 1
	player.answered_count += 1
	player.total_answer_time_ms += attempt.answer_time_ms
	player.save()


def	evaluate_current_attempt(session: GameSession) -> None:
	attempt = session.current_attempt
	if attempt is None:
		raise ValueError("No attempt to apply verdict for")
	
	attempt.is_correct = check_answer_correctness(attempt=attempt)
	attempt.evaluation_status = AnswerAttempt.EvaluationStatus.EVALUATED
	attempt.evaluated_at = timezone.now()
	attempt.save()

def apply_answer_verdict(session: GameSession) -> None:
	attempt = session.current_attempt
	if attempt is None:
		raise ValueError("No attempt to apply verdict for")

	if attempt.is_correct is None:
		raise ValueError("Attempt correctness not determined")
	
	if attempt.is_correct:
		apply_correct_answer_effects(session, attempt)
	else:
		apply_wrong_answer_effects(attempt)

	session.current_attempt = None
	session.save()

	