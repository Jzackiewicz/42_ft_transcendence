from rest_framework import serializers
from account.serializers import PublicUserSerializer


class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=500)


class GetChatHistoryInputSerializer(serializers.Serializer):
    offset = serializers.IntegerField(
        required=False, min_value=0, default=0,
        help_text="Number of messages to skip for pagination for infinite scroll. Default is 0.")


class GetChatHistoryOutputSerializer(serializers.Serializer):
    message = serializers.CharField()
    sender_username = serializers.CharField()
    timestamp = serializers.DateTimeField()


# Friend requests

class FriendRequestOutputSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    from_user = PublicUserSerializer()
    to_user = PublicUserSerializer()
    created_at = serializers.DateTimeField()


class SendFriendRequestInputSerializer(serializers.Serializer):
    to_user_id = serializers.IntegerField(
        help_text="ID of the user to send the friend request to"
    )

    def validate_to_user_id(self, value):
        request = self.context.get("request")
        if request is not None and request.user.id == value:
            raise serializers.ValidationError(
                "You can't send a friend request to yourself"
            )
        return value


class RespondFriendRequestInputSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=("accept", "decline"),
        help_text="Either 'accept' or 'decline'.",
    )


# Friendships

class FriendshipOutputSerializer(serializers.Serializer):
    friend = PublicUserSerializer()
    created_at = serializers.DateTimeField()


class FriendSearchInputSerializer(serializers.Serializer):
    q = serializers.CharField(
        min_length=2,
        max_length=150,
        help_text="Username prefix to search (min 2 characters)",
    )