from .models import ChatMessage
from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from .models import ChatMessage, Friendship, FriendRequest, RelationshipStatus

User = get_user_model()

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


# relationship status

def get_relationship_status(*, from_user: User, to_user: User) -> str:
    if Friendship.objects.filter(user=from_user, friend=to_user).exists():
        return RelationshipStatus.FRIENDS

    if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
        return RelationshipStatus.REQUEST_SENT

    if FriendRequest.objects.filter(from_user=to_user, to_user=from_user).exists():
        return RelationshipStatus.REQUEST_RECEIVED

    return RelationshipStatus.NONE


# friend search

def search_users_for_friending(*, requester: User, query: str, limit: int = 20) -> QuerySet:
    return (
        User.objects
        .filter(is_active=True, username__istartswith=query)
        .exclude(id=requester.id)
        .select_related('profile')
        .order_by('username')[:limit]
    )
