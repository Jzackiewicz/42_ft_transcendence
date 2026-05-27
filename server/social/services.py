from .models import ChatMessage
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction

from .models import ChatMessage, Friendship, FriendRequest

User = get_user_model()


# chat

def create_chat_message(room_name: str, sender_username: str, message: str) -> ChatMessage:
    chat_message = ChatMessage.objects.create(
        room_name=room_name,
        sender_username=sender_username,
        message=message
    )
    return chat_message



# friend request

def send_friend_request(*, from_user: User, to_user: User) -> FriendRequest:
    # rejects self-friendship, existing friendships, duplicate pending requests
    if from_user == to_user:
        raise ValidationError("You can't send a friend request to yourself")

    if Friendship.objects.filter(user=from_user, friend=to_user).exists():
        raise ValidationError("You are already friends with this user")

    if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
        raise ValidationError("A friend request to this user is already pending")

    if FriendRequest.objects.filter(from_user=to_user, to_user=from_user).exists():
        raise ValidationError(
            "This user has already sent you a friend request. You can accept it"
        )

    return FriendRequest.objects.create(from_user=from_user, to_user=to_user)


def accept_friend_request(*, request_id: int, to_user: User) -> Friendship:
    # Deletes the request and creates 2 friendship rows (A→B and B→A)

    with transaction.atomic():
        try:
            fr = FriendRequest.objects.get(id=request_id, to_user=to_user)
        except FriendRequest.DoesNotExist:
            raise ValidationError("Friend request is not found")

        from_user = fr.from_user
        fr.delete()

        Friendship.objects.create(user=from_user, friend=to_user)
        return Friendship.objects.create(user=to_user, friend=from_user)
    

def decline_friend_request(*, request_id: int, to_user: User) -> None:
    deleted, _ = FriendRequest.objects.filter(
        id=request_id, to_user=to_user
    ).delete()
    if not deleted:
        raise ValidationError("Friend request is not found")
    

def cancel_friend_request(*, request_id: int, from_user: User) -> None:
    deleted, _ = FriendRequest.objects.filter(
        id=request_id, from_user=from_user
    ).delete()
    if not deleted:
        raise ValidationError("Friend request is not found")
    

# friendship

def remove_friend(*, user: User, friend: User) -> None:
    # delete both rows of the friendship between user and friend
    if not Friendship.objects.filter(user=user, friend=friend).exists():
        raise ValidationError("This user is not in your friend list")

    with transaction.atomic():
        Friendship.objects.filter(user=user, friend=friend).delete()
        Friendship.objects.filter(user=friend, friend=user).delete()