from django.db import transaction
from django.db.models import Max
from game.models import GameSession, SessionPlayer
from game.selectors.lobby_selectors import get_room_by_uuid
from game.services.extra_question_generator import generate_extra_questions

from .guards import check_can_create_room, check_can_join_room, check_can_destroy_room, check_can_generate_extra_questions


def create_room(*, user) -> GameSession:
    check_can_create_room(user=user)
        
    with transaction.atomic():
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
        
    return session


def join_room(*, session_uuid: str, user) -> SessionPlayer:
    session = get_room_by_uuid(session_uuid=session_uuid)
    
    with transaction.atomic():
        session = GameSession.objects.select_for_update().get(id=session.id)

        check_can_join_room(session=session, user=user)
            
        existing_player = session.session_players.filter(user=user).first()
        if existing_player:
            return existing_player
            
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


def generate_extra_questions_for_room(*, session_uuid: str, user, n_questions_to_generate: int = 10):
    session = get_room_by_uuid(session_uuid=session_uuid)

    check_can_generate_extra_questions(session=session, user=user)
    return generate_extra_questions(session.session_uuid, n_questions_to_generate)