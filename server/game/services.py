from .fsm import GameStateMachine
from .models import GameSession, SessionPlayer, Question, AnswerAttempt
from django.db import transaction
from django.utils import timezone

def start_game_session():
	pass

@transaction.atomic
def start_answering_turn(session: GameSession) -> None:
	if session.current_player is None:
		raise ValueError("Cannot start answering turn without current player")
	
	if session.current_question is None:
		raise ValueError("Cannot start answering turn without current question")

	if session.current_attempt is not None:
		raise ValueError("Cannot start answering turn with pending attempt")

	attempt = AnswerAttempt.objects.create(
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

	session.current_attempt = attempt
	session.save()

@transaction.atomic
def submit_player_answer(session: GameSession, answer: str | None) -> None:
	
	if session.current_attempt is None:
		raise ValueError("No active attempt to submit answer for")
	
	if session.current_player is None:
		raise ValueError("Cannot submit answer without current player")

	if session.current_question is None:
		raise ValueError("Cannot submit answer without current question")

	attempt = session.current_attempt
	
	if attempt.session_id != session.id:
		raise ValueError("Current attempt does not belong to this session")

	if attempt.evaluation_status != AnswerAttempt.EvaluationStatus.PENDING:
		raise ValueError("Current attempt is not pending")

	if attempt.started_at is None:
		raise ValueError("Current attempt has no started_at")

	elapsed = timezone.now() - attempt.started_at
	answer_time_ms = max(int(elapsed.total_seconds() * 1000), 0)
	is_timeout = answer_time_ms >= session.answer_time_limit_ms

	attempt.answer_time_ms = answer_time_ms
	attempt.is_timeout = is_timeout
	if is_timeout:
		attempt.answer_text = None
	else:
		attempt.answer_text = answer
	attempt.save()

	session.fsm.submit_answer()
	session.save()

def _check_answer_correctness(attempt: AnswerAttempt) -> bool:
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

def _apply_answer_verdict(session: GameSession) -> None:
	attempt = session.current_attempt

	if attempt is None:
		raise ValueError("No attempt to apply verdict for")

	if attempt.is_correct is None:
		raise ValueError("Attempt correctness not determined")

	if attempt.is_correct:
		session.fsm.mark_correct()
	else:
		session.fsm.mark_wrong()

	session.save()
	session.fsm.resolve_evaluation()
	session.current_attempt = None
	session.save()

@transaction.atomic
def evaluate_player_answer(session: GameSession) -> None:
	attempt = session.current_attempt
	if attempt is None:
		raise ValueError("No attempt to evaluate")
	
	attempt.is_correct = _check_answer_correctness(attempt=attempt)
	attempt.evaluation_status = AnswerAttempt.EvaluationStatus.EVALUATED
	attempt.evaluated_at = timezone.now()
	attempt.save()
	_apply_answer_verdict(session=session)
	
	
def nominate_player():
	pass

def end_game_session():
	pass