from rest_framework import serializers

from .models import Question


# we don't reveal the answer
class QuestionOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'difficulty', 'is_active', 'created_at']
