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
	user_id = serializers.IntegerField(read_only=True, allow_null=True)

	class Meta:
		model = SessionPlayer
		fields = ['id', 'display_name', 'seat_number', 'lives', 'points', 'player_type', 'user_id']


class SubmitAnswerPayloadSerializer(StrictSerializer):
	answer = serializers.CharField(
		allow_null=True, allow_blank=True, required=False, default=None
	)

class NominatePlayerPayloadSerializer(StrictSerializer):
	target_player_id = serializers.IntegerField(required=True)


class GenerateExtraQuestionsPayloadSerializer(StrictSerializer):
	session_uuid = serializers.UUIDField(required=True)
	n_questions_to_generate = serializers.IntegerField(required=False, default=10, min_value=1, max_value=50)


class PlayerSnapshotSerializer(serializers.ModelSerializer):
	is_alive = serializers.BooleanField(read_only=True)
	is_online = serializers.SerializerMethodField()
	user_id = serializers.IntegerField(read_only=True, allow_null=True)
	avatar = serializers.SerializerMethodField()
	
	class Meta:
		model = SessionPlayer
		fields = [
			'id', 'display_name', 'seat_number', 'lives', 'points',
			'answered_count', 'is_alive', 'total_answer_time_ms',
			'is_online', 'user_id', 'avatar'
		]

	def get_is_online(self, obj: SessionPlayer) -> bool:
		return obj.disconnected_at is None

	def get_avatar(self, obj: SessionPlayer) -> str | None:
		if obj.user and hasattr(obj.user, 'profile'):
			return obj.user.profile.avatar_url(self.context.get('request'))
		return None

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
	players = serializers.SerializerMethodField()
	current_question = SessionQuestionSnapshotSerializer()
	current_attempt = AnswerAttemptSnapshotSerializer()
	total_questions_count = serializers.SerializerMethodField()

	class Meta:
		model = GameSession
		fields = [
			'session_uuid', 'current_status', 'host_player', 'current_player', 'last_correct_player',
			'last_nominated_player', 'players', 'current_question', 'current_attempt',
			'answer_time_limit_ms', 'nomination_time_limit_ms', 'max_players', 'winner', 'end_reason',
			'question_asked_count', 'total_questions_count',
		]

	def get_players(self, obj: GameSession):
		players = [p for p in obj.session_players.all() if p.seat_number is not None]
		return PlayerSnapshotSerializer(players, many=True).data

	def get_total_questions_count(self, obj: GameSession) -> int:
		return obj.session_questions.count()


class UserGameStatsSerializer(serializers.Serializer):
	games_played = serializers.IntegerField()
	wins = serializers.IntegerField()
	win_rate = serializers.FloatField()
	avg_score = serializers.FloatField()
	total_points = serializers.IntegerField()
	highest_score = serializers.IntegerField()
	correct_rate = serializers.FloatField()
	avg_answer_time_seconds = serializers.FloatField()



class GenerateExtraQuestionsResponseSerializer(serializers.Serializer):
    created_question_ids = serializers.ListField(
        child=serializers.IntegerField()
    )
