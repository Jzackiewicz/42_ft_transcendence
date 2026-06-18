from django.conf import settings
from django.db import models


class SessionPlayer(models.Model):
	DEFAULT_LIVES = 3

	class PlayerType(models.TextChoices):
		HUMAN = "human", "Human"
		BOT = "bot", "Bot"

	session = models.ForeignKey(
		"GameSession",
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

	seat_number = models.PositiveIntegerField(null=True, blank=True)

	lives = models.PositiveIntegerField(default=DEFAULT_LIVES)
	points = models.IntegerField(default=0)
	answered_count = models.PositiveIntegerField(default=0)
	total_answer_time_ms = models.PositiveIntegerField(default=0)
	disconnected_at = models.DateTimeField(null=True, blank=True)
	active_connections = models.PositiveIntegerField(default=0)

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
