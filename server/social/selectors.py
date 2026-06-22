from .models import ChatMessage
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from .models import ChatMessage, Friendship, FriendRequest

User = get_user_model()
PRESENCE_ROOM = "presence"
DM_ROOM_PREFIX = "dm_"

# chat

def get_chat_history_data(room_name: str, offset: int = 0) -> list[ChatMessage]:
    message_number_cap = 50
    messages = list(
        ChatMessage.objects.filter(room_name=room_name).order_by('-timestamp', '-id')[
            offset:offset + message_number_cap
        ]
    )
    messages.reverse()
    return messages


# friendships

def get_friends(*, user: User) -> QuerySet:
    #select_related pulls the friend's profile in the same query 
    return (
        Friendship.objects
        .filter(user=user)
        .select_related('friend__profile')
    )


# friend requests

def get_incoming_friend_requests(*, user: User) -> QuerySet:
    return (
        FriendRequest.objects
        .filter(to_user=user)
        .select_related('from_user__profile')
    )


def get_outgoing_friend_requests(*, user: User) -> QuerySet:
    return (
        FriendRequest.objects
        .filter(from_user=user)
        .select_related('to_user__profile')
    )


def are_friends(*, user_a_id: int, user_b_id: int) -> bool:
    return Friendship.objects.filter(
        user_id=user_a_id, friend_id=user_b_id
    ).exists()


# friend search

def search_users_for_friending(*, requester: User, query: str, limit: int = 20) -> QuerySet:
    return (
        User.objects
        .filter(is_active=True, username__istartswith=query)
        .exclude(id=requester.id)
        .select_related('profile')
        .order_by('username')[:limit]
    )


def parse_dm_room(room_name: str) -> tuple[int, int] | None:
    if not room_name.startswith(DM_ROOM_PREFIX):
        return None
    parts = room_name[len(DM_ROOM_PREFIX):].split("_")
    if len(parts) != 2:
        return None
    try:
        return (int(parts[0]), int(parts[1]))
    except ValueError:
        return None
    

def other_user_in_dm(*, room_name: str, requester_id: int) -> int | None:
    ids = parse_dm_room(room_name)
    if ids is None:
        return None
    a, b = ids
    if requester_id == a:
        return b
    if requester_id == b:
        return a
    return None
