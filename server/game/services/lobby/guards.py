from django.core.cache import cache
from django.core.exceptions import ValidationError
from rest_framework.exceptions import Throttled
from core.settings import EXTRA_QUESTION_GENERATION_MAX_PER_HOUR
from core.settings import EXTRA_QUESTION_GENERATION_CACHE_TIMEOUT_SECONDS
from django.db.models import Q
from game.models import GameSession, SessionPlayer

def _has_active_session(user, exclude_session_id: int | None = None) -> bool:
	if not user.is_authenticated:
		return False
			
	qs = SessionPlayer.objects.filter(
		user=user,
		seat_number__isnull=False
	).exclude(
		session__current_status=GameSession.Status.GAME_OVER
	)
	if exclude_session_id is not None:
		qs = qs.exclude(session_id=exclude_session_id)
		
	active_condition = Q(disconnected_at__isnull=True) | Q(
		disconnected_at__isnull=False,
		lives__gt=0
	)
	return qs.filter(active_condition).exists()

def check_can_create_room(*, user) -> None:
	if not user.is_authenticated:
		raise ValidationError("User must be authenticated to create a room.")
	if _has_active_session(user):
		raise ValidationError("Cannot create a new room while active in another game.")

def check_can_join_as_spectator(*, session: GameSession, user) -> None:
	if not user.is_authenticated:
		raise ValidationError("User must be authenticated to join a room.")
	if not session:
		raise Exception("Room not found")
	if _has_active_session(user, exclude_session_id=session.id):
		raise ValidationError("Cannot join another room while active in a game.")

def check_can_join_room(*, session: GameSession, user) -> None:
	check_can_join_as_spectator(session=session, user=user)
	if session.current_status != GameSession.Status.LOBBY:
		raise ValidationError("Cannot join a game that has already started or ended.")
	active_players = session.session_players.filter(seat_number__isnull=False).count()
	if active_players >= session.max_players:
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
def check_room_is_not_over(*, session: GameSession) -> None:
	if session.current_status == GameSession.Status.GAME_OVER:
		raise ValidationError("Cannot join a game that has already ended.")
