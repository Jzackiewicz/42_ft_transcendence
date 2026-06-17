import unicodedata
import re
from game.models import GameSession, SessionPlayer, AnswerAttempt
from django.utils import timezone
from .guards import (
	require_current_attempt,
	require_attempt_correctness_determined,
)


def normalize_string(text: str) -> str:
	"""
	Normalizes the input string by converting to lowercase, trimming whitespace,
	stripping other diacritics/accents, removing punctuation
	and collapsing multiple spaces.
	"""
	if not text:
		return ""
	text = text.lower().strip()
	text = text.replace('ł', 'l') # ł is not handled by NFKD
	nfkd_form = unicodedata.normalize('NFKD', text)
	text = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
	text = re.sub(r'[^\w\s]', '', text)
	text = " ".join(text.split())
	return text


def check_single_answer_match(correct_answer: str, player_submission: str) -> bool:
	normalized_answer = normalize_string(correct_answer)
	normalized_submission = normalize_string(player_submission)
	return normalized_answer == normalized_submission


def check_answer_correctness(attempt: AnswerAttempt) -> bool:
	if attempt.is_timeout:
		return False
	
	question = attempt.session_question.question
	correct_answer_raw = question.correct_answer or ""
	player_submission = attempt.answer_text or ""

	# Split possible correct answers by '|'
	alternatives = [alt.strip() for alt in correct_answer_raw.split("|")]

	return any(check_single_answer_match(alt, player_submission) for alt in alternatives)


def apply_correct_answer_effects(session: GameSession, attempt: AnswerAttempt) -> None:
	player = attempt.player
	if session.last_correct_player_id == player.id:
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


def evaluate_current_attempt(session: GameSession) -> None:
	require_current_attempt(session)
	attempt = session.current_attempt
	
	attempt.is_correct = check_answer_correctness(attempt=attempt)
	attempt.evaluation_status = AnswerAttempt.EvaluationStatus.EVALUATED
	attempt.evaluated_at = timezone.now()
	attempt.save()


def apply_answer_verdict(session: GameSession) -> None:
	require_current_attempt(session)
	attempt = session.current_attempt
	require_attempt_correctness_determined(attempt)
	
	if attempt.is_correct:
		apply_correct_answer_effects(session, attempt)
	else:
		apply_wrong_answer_effects(attempt)