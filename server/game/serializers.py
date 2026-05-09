from rest_framework import serializers

from .models import Question
from .models import GameSession, SessionPlayer, SessionQuestion


class GameSessionOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = ['session_uuid', 'current_status', 'max_players', 'created_at']

class SessionPlayerOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionPlayer
        fields = ['id', 'display_name', 'seat_number', 'lives', 'points', 'player_type']


class SubmitAnswerPayloadSerializer(serializers.Serializer):
    answer = serializers.CharField(
        allow_null=True, allow_blank=True, required=False, default=None
    )

class NominatePlayerPayloadSerializer(serializers.Serializer):
    target_player_id = serializers.IntegerField(required=True)


class PlayerSnapshotSerializer(serializers.ModelSerializer):
    is_alive = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SessionPlayer
        fields = ['id', 'display_name', 'seat_number', 'lives', 'points', 'answered_count', 'is_alive']

class QuestionSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        # UWAGA: Celowo omijamy 'correct_answer' by zapobiec oszustwom na frontendzie!
        fields = ['question_text', 'category']

class SessionQuestionSnapshotSerializer(serializers.ModelSerializer):
    question = QuestionSnapshotSerializer()
    
    class Meta:
        model = SessionQuestion
        fields = ['id', 'question', 'order_index']

class GameStateSnapshotSerializer(serializers.ModelSerializer):
    players = PlayerSnapshotSerializer(source='session_players', many=True)
    current_question = SessionQuestionSnapshotSerializer()

    class Meta:
        model = GameSession
        fields = [
            'session_uuid', 'current_status', 'current_player', 'last_correct_player',
            'last_nominated_player', 'players', 'current_question', 'answer_time_limit_ms',
            'winner', 'end_reason', 'question_asked_count'
        ]
