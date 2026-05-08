from rest_framework import serializers

from .models import Question
from .models import GameSession, SessionPlayer


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
