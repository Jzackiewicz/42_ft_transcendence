from django.db import models


class AnswerAttempt(models.Model):
	class EvaluationStatus(models.TextChoices):
		PENDING = "pending", "Pending"
		EVALUATED = "evaluated", "Evaluated"

	session = models.ForeignKey(
		"GameSession",
		on_delete=models.CASCADE,
		related_name="answer_attempts",
	)

	player = models.ForeignKey(
		"SessionPlayer",
		on_delete=models.CASCADE,
		related_name="answer_attempts",
	)

	session_question = models.ForeignKey(
		"SessionQuestion",
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
