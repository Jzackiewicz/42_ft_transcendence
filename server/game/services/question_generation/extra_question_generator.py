import json
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
import time
from django.db.models import Q
from django.db import transaction, IntegrityError
from django.db.models import Max
from pydantic import BaseModel
from game.models import GameSession, Question, SessionQuestion

SYSTEM_INSTRUCTION_PATH = Path(__file__).with_name("extra_question_generator_system_instruction.txt")
SYSTEM_INSTRUCTION = SYSTEM_INSTRUCTION_PATH.read_text(encoding="utf-8")

class GeneratedQuestion(BaseModel):
	category: str
	question: str
	answers: list[str]

def generate(client, model, prompt):
	for attempt in range(5):
		try:
			print("Calling " + model + "..")
			response = client.models.generate_content(
				model=model,
				contents=prompt,
				config={
					"system_instruction": SYSTEM_INSTRUCTION,
					"response_mime_type": "application/json",
					"response_schema": list[GeneratedQuestion],
				},
			)
			return response.parsed
		except Exception as e:
			if "503" in str(e):
				print("Busy servers, retrying..")
				time.sleep(2)
			else:
				raise RuntimeError("Fatal Error while generating questions") from e
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
			"answers": [session_question.question.correct_answer],
		}
		for session_question in lobby.session_questions.select_related("question").order_by("order_index")
	]
	return questions_data

def build_prompt(lobby_id, n_questions_to_generate):
	questions_data = load_lobby_questions(lobby_id)

	if not questions_data:
		return (
			f"Generate {n_questions_to_generate} general knowledge questions. "
			"The questions must not be duplicates. "
			"Return JSON array: question, answers, category."
		)

	return (
		f"Generate {n_questions_to_generate} questions based on: "
		f"{json.dumps(questions_data)}. "
		"Do not duplicate existing questions. "
		"Return JSON array: question, answers, category."
	)

def persist_generated_questions(session, generated):
	created_question_ids = []

	max_index = session.session_questions.aggregate(
		Max("order_index")
	)["order_index__max"]
	next_index = 0 if max_index is None else max_index + 1
	to_create = []
	for item in generated:
		q_text = item.question
		ans = item.answers[0] if item.answers else None
		category = item.category
		if not q_text or not ans:
			continue
		q_obj, created = Question.objects.get_or_create(
			question_text=q_text,
			defaults={
				"correct_answer": ans,
				"category": category,
				"is_ai_generated": True,
			},
		)
		if not created and not q_obj.is_ai_generated:
			q_obj.is_ai_generated = True
			q_obj.save(update_fields=["is_ai_generated"])
		if not SessionQuestion.objects.filter(
			session=session,
			question=q_obj,
		).exists():
			to_create.append(
				SessionQuestion(
					session=session,
					question=q_obj,
					order_index=next_index,
				)
			)
			next_index += 1
			created_question_ids.append(q_obj.id)
	if to_create:
		SessionQuestion.objects.bulk_create(to_create)
	return created_question_ids

def generate_extra_questions(lobby_id, n_questions_to_generate):
	load_dotenv(dotenv_path="../../../.env")
	session = GameSession.objects.filter(
		Q(pk=lobby_id) | Q(session_uuid=lobby_id)
	).first()
	if session is None:
		raise RuntimeError(f"Lobby not found: {lobby_id}")
		
	client = genai.Client(api_key=os.environ["LLM_API_KEY"])
	prompt = build_prompt(lobby_id, n_questions_to_generate)
	generated = generate(
		client,
		os.environ["LLM_MODEL"],
		prompt,
	)

	created_question_ids = persist_generated_questions(session, generated)
	return {"created_question_ids": created_question_ids}
	