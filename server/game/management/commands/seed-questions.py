from django.core.management.base import BaseCommand
from game.models import Question

class Command(BaseCommand):
	help = "Seeds the database with a basic set of 20 trivia questions for testing game logic"

	def handle(self, *args, **options):
		questions_data = [
			{"question_text": "What is 2 + 2?", "correct_answer": "4", "category": "math"},
			{"question_text": "What is the capital of Poland?", "correct_answer": "Warsaw", "category": "geography"},
			{"question_text": "What is the capital of France?", "correct_answer": "Paris", "category": "geography"},
			{"question_text": "What is the color of the sky on a clear day?", "correct_answer": "blue", "category": "general"},
			{"question_text": "What is the largest ocean on Earth?", "correct_answer": "Pacific", "category": "geography"},
			{"question_text": "How many days are in a leap year?", "correct_answer": "366", "category": "general"},
			{"question_text": "What is the capital of Germany?", "correct_answer": "Berlin", "category": "geography"},
			{"question_text": "What is the capital of the United Kingdom?", "correct_answer": "London", "category": "geography"},
			{"question_text": "How many legs does a spider have?", "correct_answer": "8", "category": "animals"},
			{"question_text": "What planet is closest to the Sun?", "correct_answer": "Mercury", "category": "science"},
			{"question_text": "What is the capital of Italy?", "correct_answer": "Rome", "category": "geography"},
			{"question_text": "What is the capital of Spain?", "correct_answer": "Madrid", "category": "geography"},
			{"question_text": "What gas do humans need to breathe to live?", "correct_answer": "oxygen", "category": "science"},
			{"question_text": "What is 5 + 5?", "correct_answer": "10", "category": "math"},
			{"question_text": "Who is the most handsome man alive?", "correct_answer": "Damian Bozic", "category": "general"},
			{"question_text": "What chemical formula represents water?", "correct_answer": "h2o", "category": "science"},
			{"question_text": "What is the capital of Japan?", "correct_answer": "Tokyo", "category": "geography"},
			{"question_text": "How many hours are in a day?", "correct_answer": "24", "category": "general"},
			{"question_text": "What is the largest planet in our solar system?", "correct_answer": "Jupiter", "category": "science"},
			{"question_text": "What is the currency of the United States?", "correct_answer": "dollar", "category": "general"},
		]

		created_count = 0
		for q_data in questions_data:
			obj, created = Question.objects.get_or_create(
				question_text=q_data["question_text"],
				defaults={
					"correct_answer": q_data["correct_answer"],
					"category": q_data["category"]
				}
			)
			if created:
				created_count += 1
				self.stdout.write(self.style.SUCCESS(f"Created: '{obj.question_text}' -> '{obj.correct_answer}'"))

		self.stdout.write(
			self.style.SUCCESS(
				f"Successfully seeded database. Created {created_count} new questions (total in DB: {Question.objects.count()})."
			)
		)
