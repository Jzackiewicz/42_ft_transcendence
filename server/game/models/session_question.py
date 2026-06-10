from django.db import models


class SessionQuestion(models.Model):
	session = models.ForeignKey(
		"GameSession",
		on_delete=models.CASCADE,
		related_name="session_questions",
	)

	question = models.ForeignKey(
		"Question",
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
