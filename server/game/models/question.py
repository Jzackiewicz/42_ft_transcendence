from django.db import models


class Question(models.Model):
	question_text = models.TextField()
	correct_answer = models.TextField()
	category = models.CharField(default='any', max_length=100)
	is_ai_generated = models.BooleanField(default=False)
	def __str__(self) -> str:
		return f"Question<{self.id}> category={self.category}"
