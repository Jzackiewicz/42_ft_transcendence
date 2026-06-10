from django.core.cache import cache
from django.core.exceptions import ValidationError
from rest_framework.exceptions import Throttled
from game.models import GameSession
from core.settings import EXTRA_QUESTION_GENERATION_MAX_PER_HOUR
from core.settings import EXTRA_QUESTION_GENERATION_CACHE_TIMEOUT_SECONDS

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


def check_can_generate_extra_questions(*, session: GameSession, user) -> None:
	if not user.is_authenticated:
		raise ValidationError("User must be authenticated to generate extra questions.")
	if not session:
		raise LookupError("Room not found")
	if session.host_player is None or session.host_player.user != user:
		raise ValidationError("Only the host can generate extra questions.")
	if session.current_status != GameSession.Status.LOBBY:
		raise ValidationError("Cannot generate extra questions once the game has started.")


def reserve_extra_question_generation_quota(*, user) -> None:
	quota_key = f"game:extra_questions:{user.id}"
	if cache.add(quota_key, 1, timeout=EXTRA_QUESTION_GENERATION_CACHE_TIMEOUT_SECONDS):
		current_total = 1
	else:
		current_total = cache.incr(quota_key)

	if current_total > EXTRA_QUESTION_GENERATION_MAX_PER_HOUR:
		cache.decr(quota_key)
		raise Throttled(
			detail=(
				f"You can generate extra questions at most {EXTRA_QUESTION_GENERATION_MAX_PER_HOUR} times per hour."
			),
			wait=EXTRA_QUESTION_GENERATION_CACHE_TIMEOUT_SECONDS,
		)


def release_extra_question_generation_quota(*, user) -> None:
	quota_key = f"game:extra_questions:{user.id}"
	current_total = cache.get(quota_key)
	if current_total is None:
		return
	if current_total <= 1:
		cache.delete(quota_key)
	else:
		cache.decr(quota_key)