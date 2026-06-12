from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema
from django.core.exceptions import ValidationError
from account.selectors import user_get_by_id
from account.serializers import PublicUserSerializer
from .selectors import (
    get_chat_history_data,
    get_friends,
    get_incoming_friend_requests,
    get_outgoing_friend_requests,
    get_relationship_status,
    search_users_for_friending,
)
from .serializers import (
    FriendRequestOutputSerializer,
    FriendSearchInputSerializer,
    FriendshipOutputSerializer,
    GetChatHistoryInputSerializer,
    GetChatHistoryOutputSerializer,
    RelationshipStatusOutputSerializer,
    RespondFriendRequestInputSerializer,
    SendFriendRequestInputSerializer,
)
from .services import (
    accept_friend_request,
    cancel_friend_request,
    decline_friend_request,
    remove_friend,
    send_friend_request,
)
from social.presence import PresenceRegistry

# from .services import

"""
This module is for API endpoints, controllers, views.
In a Zero Trust architecture, this layer is responsible for handling incoming HTTP requests, validating them, and then delegating to the appropriate services or selectors.
It should not contain any business logic or direct database access; instead, it should focus on request/response handling and input validation.
"""

# chat

class ChatHistoryApi(APIView):

    @extend_schema(
        parameters=[GetChatHistoryInputSerializer],
        responses={200: GetChatHistoryOutputSerializer(many=True)},
        description="GET endpoint to retrieve chatroom history."
    )
    def get(self, request, room_name: str):
        input_serializer = GetChatHistoryInputSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)

        chat_history_batch = get_chat_history_data(room_name=room_name, **input_serializer.validated_data)

        output_serializer = GetChatHistoryOutputSerializer(chat_history_batch, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)



# friend requests

class FriendRequestCollectionApi(APIView):
    """POST /social/friend-requests/  — send a friend request."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=SendFriendRequestInputSerializer,
        responses={201: FriendRequestOutputSerializer},
        description="Send a friend request to another user.",
    )
    def post(self, request):
        input_serializer = SendFriendRequestInputSerializer(
            data=request.data, context={"request": request}
        )
        input_serializer.is_valid(raise_exception=True)

        to_user = user_get_by_id(user_id=input_serializer.validated_data["to_user_id"])

        try:
            friend_request = send_friend_request(
                from_user=request.user, to_user=to_user
            )
        except ValidationError as e:
            return Response({"error": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

        output = FriendRequestOutputSerializer(friend_request, context={"request": request})
        return Response(output.data, status=status.HTTP_201_CREATED)
    

class FriendRequestIncomingApi(APIView):
    """GET /social/friend-requests/incoming/"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: FriendRequestOutputSerializer(many=True)},
        description="Pending friend requests received by the authenticated user.",
    )
    def get(self, request):
        requests_qs = get_incoming_friend_requests(user=request.user)
        output = FriendRequestOutputSerializer(
            requests_qs, many=True, context={"request": request}
        )
        return Response(output.data, status=status.HTTP_200_OK)
    

class FriendRequestOutgoingApi(APIView):
    """GET /social/friend-requests/outgoing/"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: FriendRequestOutputSerializer(many=True)},
        description="Pending friend requests sent by the authenticated user.",
    )
    def get(self, request):
        requests_qs = get_outgoing_friend_requests(user=request.user)
        output = FriendRequestOutputSerializer(
            requests_qs, many=True, context={"request": request}
        )
        return Response(output.data, status=status.HTTP_200_OK)
    

class FriendRequestDetailApi(APIView):
    """PATCH  /social/friend-requests/<id>/  — accept or decline (receiver).
    DELETE /social/friend-requests/<id>/  — cancel (sender)."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=RespondFriendRequestInputSerializer,
        responses={
            200: FriendshipOutputSerializer, # action='accept'
            204: None, # action='decline'
        },
        description="Accept or decline a friend request addressed to you.",
    )
    def patch(self, request, request_id: int):
        input_serializer = RespondFriendRequestInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        action = input_serializer.validated_data["action"]

        try:
            if action == "accept":
                friendship = accept_friend_request(
                    request_id=request_id, to_user=request.user
                )
                output = FriendshipOutputSerializer(friendship, context={"request": request})
                return Response(output.data, status=status.HTTP_200_OK)

            # action == "decline" — ChoiceField already excluded anything else
            decline_friend_request(request_id=request_id, to_user=request.user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"error": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: None},
        description="Cancel a friend request you sent.",
    )
    def delete(self, request, request_id: int):
        try:
            cancel_friend_request(request_id=request_id, from_user=request.user)
        except ValidationError as e:
            return Response({"error": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# friendship

class FriendListApi(APIView):
    """GET /social/friends/"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: FriendshipOutputSerializer(many=True)},
        description="List the authenticated user's friends.",
    )
    def get(self, request):
        friends = list(get_friends(user=request.user))

        friend_ids = [f.friend_id for f in friends]
        online = PresenceRegistry.online_user_ids(friend_ids)

        output = FriendshipOutputSerializer(
            friends, many=True, context={"request": request, "online_user_ids": online }
        )
        return Response(output.data, status=status.HTTP_200_OK)
    

class FriendDetailApi(APIView):
    """DELETE /social/friends/<user_id>/ — unfriend."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={204: None},
        description="Remove a user from your friend list.",
    )
    def delete(self, request, user_id: int):
        friend = user_get_by_id(user_id=user_id)
        try:
            remove_friend(user=request.user, friend=friend)
        except ValidationError as e:
            return Response({"error": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class FriendSearchApi(APIView):
    """GET /social/friends/search/?q=alice"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[FriendSearchInputSerializer],
        responses={200: PublicUserSerializer(many=True)},
        description="Username prefix search for the add-a-friend autocomplete.",
    )
    def get(self, request):
        input_serializer = FriendSearchInputSerializer(data=request.query_params)
        input_serializer.is_valid(raise_exception=True)

        users = search_users_for_friending(
            requester=request.user, query=input_serializer.validated_data["q"]
        )
        output = PublicUserSerializer(users, many=True, context={"request": request})
        return Response(output.data, status=status.HTTP_200_OK)
    

# relationship status

class RelationshipStatusApi(APIView):
    """GET /social/relationship/<user_id>/"""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: RelationshipStatusOutputSerializer},
        description="Get the relationship between the authenticated user and another user.",
    )
    def get(self, request, user_id: int):
        other_user = user_get_by_id(user_id=user_id)
        relationship_status = get_relationship_status(
            from_user=request.user, to_user=other_user
        )
        output = RelationshipStatusOutputSerializer({"status": relationship_status})
        return Response(output.data, status=status.HTTP_200_OK)