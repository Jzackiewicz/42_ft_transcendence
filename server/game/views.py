from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from .selectors import question_get_by_id, question_list
from .serializers import (
    QuestionGenerationRequestSerializer,
    QuestionGenerationResponseSerializer,
    QuestionOutputSerializer,
)

# ---------------------------------------------------------------------------
# Question endpoints — read-only.
# Questions are managed exclusively through the Django admin.
# ---------------------------------------------------------------------------

class QuestionListApi(APIView):

    @extend_schema(
        responses={200: QuestionOutputSerializer(many=True)},
        description="List all active questions.",
    )
    def get(self, request):
        questions = question_list()
        output_serializer = QuestionOutputSerializer(questions, many=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class QuestionDetailApi(APIView):

    @extend_schema(
        responses={200: QuestionOutputSerializer},
        description="Retrieve a single question by ID.",
    )
    def get(self, request, question_id: int):
        question = question_get_by_id(question_id=question_id)
        output_serializer = QuestionOutputSerializer(question)
        return Response(output_serializer.data, status=status.HTTP_200_OK)


