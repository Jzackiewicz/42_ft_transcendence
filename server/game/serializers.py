from rest_framework import serializers

from .models import Question
from .models import GameSession, SessionPlayer, SessionQuestion, AnswerAttempt


class StrictSerializer(serializers.Serializer):
	def validate(self, attrs):
		unknown_fields = set(self.initial_data) - set(self.fields)
		if unknown_fields:
			raise serializers.ValidationError({
				field: ["Unknown field."]
				for field in sorted(unknown_fields)
			})
		return attrs


class GameSessionOutputSerializer(serializers.ModelSerializer):
	class Meta:
		model = GameSession
		fields = ['session_uuid', 'current_status', 'max_players', 'created_at']

class SessionPlayerOutputSerializer(serializers.ModelSerializer):
	class Meta:
		model = SessionPlayer
		fields = ['id', 'display_name', 'seat_number', 'lives', 'points', 'player_type']


class SubmitAnswerPayloadSerializer(StrictSerializer):
	answer = serializers.CharField(
		allow_null=True, allow_blank=True, required=False, default=None
	)

class NominatePlayerPayloadSerializer(StrictSerializer):
	target_player_id = serializers.IntegerField(required=True)


class PlayerSnapshotSerializer(serializers.ModelSerializer):
	is_alive = serializers.BooleanField(read_only=True)
	
	class Meta:
		model = SessionPlayer
		fields = ['id', 'display_name', 'seat_number', 'lives', 'points', 'answered_count', 'is_alive', 'total_answer_time_ms']

class QuestionSnapshotSerializer(serializers.ModelSerializer):
	class Meta:
		model = Question
		fields = ['question_text', 'category']

class SessionQuestionSnapshotSerializer(serializers.ModelSerializer):
	question = QuestionSnapshotSerializer()
	
	class Meta:
		model = SessionQuestion
		fields = ['id', 'question', 'order_index']


class AnswerAttemptSnapshotSerializer(serializers.ModelSerializer):
	correct_answer = serializers.SerializerMethodField()
	player = serializers.PrimaryKeyRelatedField(read_only=True)

	class Meta:
		model = AnswerAttempt
		fields = [
			'id', 'answer_text', 'is_timeout', 'is_correct',
			'evaluation_status', 'correct_answer', 'player', 'evaluated_at'
		]

	def get_correct_answer(self, obj: AnswerAttempt) -> str | None:
		if (
			obj.evaluation_status == AnswerAttempt.EvaluationStatus.EVALUATED
			and obj.session.current_status == GameSession.Status.EVALUATION
		):
			return obj.session_question.question.correct_answer
		return None


class GameStateSnapshotSerializer(serializers.ModelSerializer):
	players = PlayerSnapshotSerializer(source='session_players', many=True)
	current_question = SessionQuestionSnapshotSerializer()
	current_attempt = AnswerAttemptSnapshotSerializer()
	total_questions_count = serializers.SerializerMethodField()

	class Meta:
		model = GameSession
		fields = [
			'session_uuid', 'current_status', 'host_player', 'current_player', 'last_correct_player',
			'last_nominated_player', 'players', 'current_question', 'current_attempt',
			'answer_time_limit_ms', 'winner', 'end_reason', 'question_asked_count',
			'total_questions_count',
		]

	def get_total_questions_count(self, obj: GameSession) -> int:
		return obj.session_questions.count()
