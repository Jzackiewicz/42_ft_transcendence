from rest_framework import serializers

from .models import Question


class QuestionOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "question_text", "category"]


class QuestionGenerationRequestSerializer(serializers.Serializer):
    category = serializers.CharField(max_length=100)
    question_count = serializers.IntegerField(min_value=1, max_value=200)


class GeneratedQuestionSerializer(serializers.Serializer):
    category = serializers.CharField()
    question = serializers.CharField()
    answer = serializers.ListField(child=serializers.CharField())


class QuestionGenerationResponseSerializer(serializers.Serializer):
    requested_category = serializers.CharField()
    question_count = serializers.IntegerField()
    questions = GeneratedQuestionSerializer(many=True)
