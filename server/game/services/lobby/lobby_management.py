from django.db import transaction
from django.db.models import Max
from game.models import GameSession, SessionPlayer
from game.selectors.lobby_selectors import get_room_by_uuid
from game.services.game_flow.lifecycle import handle_disconnect_in_lobby
from game.services.game_flow.game_action_handler import GameActionHandler
from .guards import check_can_create_room, check_can_join_room, check_can_destroy_room
from game.services.game_flow.lifecycle import assign_random_questions_to_session


def _cleanup_and_sync_other_sessions(user, exclude_session_id: int | None = None) -> None:
    if not user or not user.is_authenticated:
        return

    active_sessions = GameSession.objects.filter(
        session_players__user=user
    ).exclude(current_status=GameSession.Status.GAME_OVER)

    if exclude_session_id is not None:
        active_sessions = active_sessions.exclude(id=exclude_session_id)

    handler = GameActionHandler()
    for session in active_sessions:
        try:
            if session.current_status == GameSession.Status.LOBBY:
                player = session.session_players.filter(user=user).first()
                if player:
                    handle_disconnect_in_lobby(session, player)
            else:
                handler.sync_game_disconnections(session.id)
        except Exception:
            pass


def create_room(*, user) -> GameSession:
    with transaction.atomic():
        _cleanup_and_sync_other_sessions(user)
        check_can_create_room(user=user)
        
        session = GameSession.objects.create(
            current_status=GameSession.Status.LOBBY
        )
        
        player = SessionPlayer.objects.create(
            session=session,
            user=user,
            display_name=getattr(user, 'username', f'User_{user.id}'),
            seat_number=1,
            player_type=SessionPlayer.PlayerType.HUMAN
        )
        
        session.host_player = player
        session.save(update_fields=['host_player'])
        
        assign_random_questions_to_session(session)
        
    return session


def join_room(*, session_uuid: str, user) -> SessionPlayer:
    session = get_room_by_uuid(session_uuid=session_uuid)
    
    with transaction.atomic():
        session = GameSession.objects.select_for_update().get(id=session.id)

        if user.is_authenticated:
            existing_player = session.session_players.filter(user=user).first()
            if existing_player:
                return existing_player

            _cleanup_and_sync_other_sessions(user, exclude_session_id=session.id)

        check_can_join_room(session=session, user=user)
            
        max_seat = session.session_players.aggregate(Max('seat_number'))['seat_number__max'] or 0
        
        player = SessionPlayer.objects.create(
            session=session,
            user=user,
            display_name=getattr(user, 'username', f'User_{user.id}'),
            seat_number=max_seat + 1,
            player_type=SessionPlayer.PlayerType.HUMAN
        )
        
    return player


def destroy_room(*, session_uuid: str, user) -> None:
    session = get_room_by_uuid(session_uuid=session_uuid)
    
    check_can_destroy_room(session=session, user=user)
    session.delete()