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
from .services.question_generator import generate_questions


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


class QuestionGenerateApi(APIView):

    @extend_schema(
        request=QuestionGenerationRequestSerializer,
        responses={200: QuestionGenerationResponseSerializer},
        description="Generate AI-backed questions for a category and question count.",
    )
    def post(self, request):
        input_serializer = QuestionGenerationRequestSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        payload = generate_questions(
            category=input_serializer.validated_data["category"],
            question_count=input_serializer.validated_data["question_count"],
        )

        output_serializer = QuestionGenerationResponseSerializer(data=payload)
        output_serializer.is_valid(raise_exception=True)
        return Response(output_serializer.data, status=status.HTTP_200_OK)
