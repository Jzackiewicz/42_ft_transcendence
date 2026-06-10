import uuid

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
	nomination_time_limit_ms = models.PositiveIntegerField(default=10000)
	nomination_started_at = models.DateTimeField(null=True, blank=True)
	
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
