import uuid

from django.conf import settings
from django.db import models
from statemachine.mixins import MachineMixin
import game.fsm


class GameSession(MachineMixin, models.Model):
	class Status(models.TextChoices):
		LOBBY = "lobby", "Lobby"
		ANSWERING = "answering", "Answering"
		EVALUATION = "evaluation", "Evaluation"
		NOMINATION = "nomination", "Nomination"
		GAME_OVER = "game_over", "Game Over"

	class EndReason(models.TextChoices):
		LAST_PLAYER_ALIVE = "last_player_alive", "Last player alive"
		QUESTIONS_EXHAUSTED = "questions_exhausted", "Questions exhausted"
		CANCELLED = "cancelled", "Cancelled"

	session_uuid = models.UUIDField(default=uuid.uuid4, unique=True)

	host_player = models.ForeignKey(
		"SessionPlayer",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="hosted_sessions",
	)

	current_status = models.CharField(
		max_length=32,
		choices=Status.choices,
		default=Status.LOBBY,
	)

	current_player = models.ForeignKey(
		"SessionPlayer",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="sessions_where_current",
	)

	last_correct_player = models.ForeignKey(
		"SessionPlayer",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="sessions_where_last_correct",
	)

	last_nominated_player = models.ForeignKey(
		"SessionPlayer",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="sessions_where_last_nominated",
	)

	current_question = models.ForeignKey(
		"SessionQuestion",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)

	current_attempt = models.ForeignKey(
		"AnswerAttempt",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)

	winner = models.ForeignKey(
		"SessionPlayer",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="won_sessions",
	)

	end_reason = models.CharField(
		max_length=64,
		choices=EndReason.choices,
		null=True,
		blank=True,
	)

	question_asked_count = models.PositiveIntegerField(default=0)

	created_at = models.DateTimeField(auto_now_add=True)
	started_at = models.DateTimeField(null=True, blank=True)
	ended_at = models.DateTimeField(null=True, blank=True)


	answer_time_limit_ms = models.PositiveIntegerField(default=20000)
	evaluation_time_limit_ms = models.PositiveIntegerField(default=3000)
	# starting_lives = models.PositiveIntegerField(default=3)
	max_players = models.PositiveIntegerField(default=5)

	state_machine_name = "game.fsm.GameStateMachine"
	state_machine_attr = "fsm"
	state_field_name = "current_status"

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:
		return f"GameSession<{self.id}> status={self.current_status}"

	def has_last_correct_player_alive(self) -> bool:
		if self.last_correct_player_id is None:
			return False

		return self.session_players.filter(
			id=self.last_correct_player_id,
			lives__gt=0,
		).exists()
	
	def is_game_over(self) -> bool:
		alive_players = self.session_players.filter(lives__gt=0).count()
		questions_exhausted = self.question_asked_count >= self.session_questions.count()
		return alive_players <= 1 or questions_exhausted

class SessionPlayer(models.Model):
	class PlayerType(models.TextChoices):
		HUMAN = "human", "Human"
		BOT = "bot", "Bot"

	session = models.ForeignKey(
		GameSession,
		on_delete=models.CASCADE,
		related_name="session_players",
	)

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="game_session_players",
	)

	player_type = models.CharField(
		max_length=16,
		choices=PlayerType.choices,
		default=PlayerType.HUMAN,
	)

	display_name = models.CharField(max_length=100)

	seat_number = models.PositiveIntegerField()

	lives = models.PositiveIntegerField(default=3)
	points = models.IntegerField(default=0)
	answered_count = models.PositiveIntegerField(default=0)
	total_answer_time_ms = models.PositiveIntegerField(default=0)

	class Meta:
		ordering = ["session_id", "seat_number"]
		constraints = [
			models.UniqueConstraint(
				fields=["session", "seat_number"],
				name="unique_seat_number_per_session",
			),
			models.UniqueConstraint(
				fields=["session", "user"],
				condition=models.Q(user__isnull=False),
				name="unique_human_user_per_session",
			),
		]

	def __str__(self) -> str:
		return f"SessionPlayer<{self.id}> {self.display_name} in session {self.session_id}"

	@property
	def is_alive(self) -> bool:
		return self.lives > 0


class Question(models.Model):
	question_text = models.TextField()
	correct_answer = models.TextField()
	category = models.CharField(default='any', max_length=100)
	def __str__(self) -> str:
		return f"Question<{self.id}> category={self.category}"


class SessionQuestion(models.Model):
	session = models.ForeignKey(
		GameSession,
		on_delete=models.CASCADE,
		related_name="session_questions",
	)

	question = models.ForeignKey(
		Question,
		on_delete=models.PROTECT,
		related_name="session_questions",
	)

	order_index = models.PositiveIntegerField()

	class Meta:
		ordering = ["session_id", "order_index"]
		constraints = [
			models.UniqueConstraint(
				fields=["session", "order_index"],
				name="unique_question_order_per_session",
			),
			models.UniqueConstraint(
				fields=["session", "question"],
				name="unique_question_once_per_session",
			),
		]

	def __str__(self) -> str:
		return f"SessionQuestion<{self.id}> session={self.session_id} order={self.order_index}"


class AnswerAttempt(models.Model):
	class EvaluationStatus(models.TextChoices):
		PENDING = "pending", "Pending"
		EVALUATED = "evaluated", "Evaluated"

	session = models.ForeignKey(
		GameSession,
		on_delete=models.CASCADE,
		related_name="answer_attempts",
	)

	player = models.ForeignKey(
		SessionPlayer,
		on_delete=models.CASCADE,
		related_name="answer_attempts",
	)

	session_question = models.ForeignKey(
		SessionQuestion,
		on_delete=models.CASCADE,
		related_name="answer_attempts",
	)

	answer_text = models.TextField(null=True, blank=True)
	is_timeout = models.BooleanField(default=False)
	is_correct = models.BooleanField(null=True, blank=True)

	evaluation_status = models.CharField(
		max_length=16,
		choices=EvaluationStatus.choices,
		default=EvaluationStatus.PENDING,
	)

	answer_time_ms = models.PositiveIntegerField(default=0)

	created_at = models.DateTimeField(auto_now_add=True)
	started_at = models.DateTimeField(null=True, blank=True)
	evaluated_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ["id"]

	def __str__(self) -> str:
		parts = [
			f"AnswerAttempt<{self.id}>",
			f"player={self.player_id}",
			f"q={self.session_question_id}",
			f"status={self.evaluation_status}",
		]

		if self.evaluation_status == self.EvaluationStatus.EVALUATED:
			parts.append(f"correct={self.is_correct}")
			parts.append(f"timeout={self.is_timeout}")

		return " ".join(parts)