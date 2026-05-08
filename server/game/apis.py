from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from .services.lobby.lobby_management import create_room, join_room, destroy_room
from .serializers import GameSessionOutputSerializer, SessionPlayerOutputSerializer


class RoomCreateApi(APIView):
	@extend_schema(
		request=None,
		responses={201: GameSessionOutputSerializer},
		description="Create a new game lobby."
	)
	def post(self, request):
		try:
			session = create_room(user=request.user)
			serializer = GameSessionOutputSerializer(session)
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		except ValidationError as e:
			return Response({"error": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)


class RoomJoinApi(APIView):
	@extend_schema(
		request=None,
		responses={200: SessionPlayerOutputSerializer},
		description="Join an existing game lobby by UUID."
	)
	def post(self, request, session_uuid):
		try:
			player = join_room(session_uuid=session_uuid, user=request.user)
			serializer = SessionPlayerOutputSerializer(player)
			return Response(serializer.data, status=status.HTTP_200_OK)
		except ValidationError as e:
			return Response({"error": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
		except Exception:
			return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)


class RoomDestroyApi(APIView):
	@extend_schema(
		request=None,
		responses={204: None},
		description="Destroy a game lobby (host only)."
	)
	def delete(self, request, session_uuid):
		try:
			destroy_room(session_uuid=session_uuid, user=request.user)
			return Response(status=status.HTTP_204_NO_CONTENT)
		except ValidationError as e:
			return Response({"error": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
		except Exception:
			return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
