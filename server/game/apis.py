from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiTypes
from rest_framework.exceptions import Throttled
from google.genai.errors import APIError
from rest_framework.permissions import IsAuthenticated

from .services.lobby.lobby_management import create_room, join_room, destroy_room, generate_extra_questions_for_room
from .serializers import (
	GameSessionOutputSerializer,
	SessionPlayerOutputSerializer,
	GenerateExtraQuestionsPayloadSerializer,
	GenerateExtraQuestionsResponseSerializer,
	UserGameStatsSerializer,
)
from .selectors.stats_selectors import get_user_game_stats

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


class UserGameStatsApi(APIView):
	permission_classes = [IsAuthenticated]

	@extend_schema(
		request=None,
		responses={200: UserGameStatsSerializer},
		description="Retrieve game statistics for a specific user by ID."
	)
	def get(self, request, user_id):
		stats = get_user_game_stats(user_id=user_id)
		serializer = UserGameStatsSerializer(stats)
		return Response(serializer.data, status=status.HTTP_200_OK)


class GenerateExtraQuestionsApi(APIView):
	@extend_schema(
		request=GenerateExtraQuestionsPayloadSerializer,
		responses={
			200: GenerateExtraQuestionsResponseSerializer,
		},
		description="Generate extra questions for a lobby (host only)."
	)
	def post(self, request):
		serializer = GenerateExtraQuestionsPayloadSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		try:
			data = generate_extra_questions_for_room(
				session_uuid=serializer.validated_data["session_uuid"],
				user=request.user,
			)
			output_serializer = GenerateExtraQuestionsResponseSerializer(data=data)
			output_serializer.is_valid(raise_exception=True)
			return Response(output_serializer.data, status=status.HTTP_200_OK)
		except Throttled as e:
			response = Response({"error": str(e.detail)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
			if e.wait:
				response["Retry-After"] = str(int(e.wait))
			return response
		except ValidationError as e:
			return Response({"error": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)
		except LookupError:
			return Response({"error": "Room not found"}, status=status.HTTP_404_NOT_FOUND)
		except (APIError, RuntimeError) as e:
			return Response({"error": f"AI service error: {e}"}, status=status.HTTP_502_BAD_GATEWAY)
