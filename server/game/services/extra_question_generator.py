import json
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
import time
from django.db.models import Q
from django.db import transaction, IntegrityError
from django.db.models import Max

from game.models import GameSession, Question, SessionQuestion

SYSTEM_INSTRUCTION_PATH = Path(__file__).with_name("extra_question_generator_system_instruction.txt")
SYSTEM_INSTRUCTION = SYSTEM_INSTRUCTION_PATH.read_text(encoding="utf-8")

def generate(client, model, prompt):
	success = False
	for attempt in range (5):
		try:
			print("Calling " + model + "..")
			response = client.models.generate_content(
				model=model,
				contents=prompt,
				config={
					"system_instruction": SYSTEM_INSTRUCTION,
					"response_mime_type": "application/json"
				}
			)
			success = True
			data = json.loads(response.text)
			return data
		except Exception as e:
			if "503" in str(e):
				print("Busy servers, retrying..")
				time.sleep(2)
			else:
				print("Fatal Error:", e)
				raise RuntimeError("Fatal Error while generating questions") from e
	if not success:
		print("Stopping retries, servers are too busy.")
		raise RuntimeError("Stopping retries, servers are too busy.")

def load_lobby_questions(lobby_id):
	"""Takes a lobby ID and returns a data object containing the questions, their answers, and a category for each question."""
	lobby = GameSession.objects.filter(
		Q(pk=lobby_id) | Q(session_uuid=lobby_id)
	).first()
	if lobby is None:
		raise RuntimeError(f"Lobby not found: {lobby_id}")
	questions_data = [
		{
			"category": session_question.question.category,
			"question": session_question.question.question_text,
			"answer": [session_question.question.correct_answer],
		}
		for session_question in lobby.session_questions.select_related("question").order_by("order_index")
	]
	if not questions_data:
		raise RuntimeError(f"Lobby has no questions: {lobby_id}")
	return questions_data

def generate_extra_questions(lobby_id, n_questions_to_generate):
	# Load existing lobby questions to provide context to the LLM
	questions_data = load_lobby_questions(lobby_id)
	prompt = (
		"Generate "
		+ str(n_questions_to_generate)
		+ " questions and answers based off of the following questions: "
		+ json.dumps(questions_data)
		+ ". The questions must not be duplicates of the ones given. Return a JSON array of objects with keys: question, answer (or answers), category."
	)
	print("About to generate extra questions..")
	load_dotenv(dotenv_path="../../../.env")
	client = genai.Client(api_key=os.environ["LLM_API_KEY"])
	data = generate(client, "gemini-3.1-flash-lite", prompt)

	# Normalize the LLM response into a list of question dicts
	def _extract_question_list(obj):
		if obj is None:
			return []
		if isinstance(obj, list):
			return obj
		if isinstance(obj, dict):
			# Common wrapper keys
			for k in ("questions", "results", "items"):
				if k in obj and isinstance(obj[k], list):
					return obj[k]
			# If the dict itself looks like a single question, wrap it
			# e.g. {"question":..., "answer":...}
			if any(key in obj for key in ("question", "question_text", "q")):
				return [obj]
		return []

	generated = _extract_question_list(data)

	# Persist generated questions and attach to the session
	session = GameSession.objects.filter(Q(pk=lobby_id) | Q(session_uuid=lobby_id)).first()
	if session is None:
		raise RuntimeError(f"Lobby not found: {lobby_id}")

	created_question_ids = []
	with transaction.atomic():
		# determine starting order index
		max_index = session.session_questions.aggregate(Max("order_index"))["order_index__max"]
		next_index = 0 if max_index is None else max_index + 1

		session_questions_to_create = []
		for item in generated:
			# tolerant field extraction
			q_text = (
				item.get("question") if isinstance(item, dict) else None
			) or (
				item.get("question_text") if isinstance(item, dict) else None
			) or (
				item.get("q") if isinstance(item, dict) else None
			)

			ans = None
			if isinstance(item, dict):
				a = item.get("answer") or item.get("answers") or item.get("correct_answer")
				if isinstance(a, list) and a:
					ans = a[0]
				elif isinstance(a, str):
					ans = a

			category = (
				item.get("category") if isinstance(item, dict) else None
			) or "any"

			if not q_text or not ans:
				continue

			# create or get Question
			q_obj, created = Question.objects.get_or_create(
				question_text=q_text,
				defaults={
					"correct_answer": ans,
					"category": category,
					"is_ai_generated": True,
				},
			)
			if not created and not q_obj.is_ai_generated:
				# mark existing question as AI-generated if appropriate
				q_obj.is_ai_generated = True
				q_obj.save(update_fields=["is_ai_generated"])

			# attach to session if not already present
			if not SessionQuestion.objects.filter(session=session, question=q_obj).exists():
				sq = SessionQuestion(session=session, question=q_obj, order_index=next_index)
				session_questions_to_create.append(sq)
				next_index += 1
				created_question_ids.append(q_obj.id)

		if session_questions_to_create:
			SessionQuestion.objects.bulk_create(session_questions_to_create)

	return {"created_question_ids": created_question_ids}

# remove gemini as a magic number, have it defined in .env
# create a fake lobby filled with questions, answers and categories in order to inject into this function for testing
# think about how emulate it, perhaps you need to populate the database with a lobby
# call POST from SWAGGER while using this emulated lobby
# respond to the POST request with the generated question IDs so that the lobby can fetch them and display to the user
