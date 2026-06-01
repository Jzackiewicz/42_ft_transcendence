import json
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
import time
from django.db.models import Q

from game.models import GameSession

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
	questions_data = load_lobby_questions(lobby_id)
	prompt = "Generate " + str(n_questions_to_generate) + " questions and answers based off of the following questions: " + json.dumps(questions_data) + ". The questions must not be duplicates of the ones given."
	print("About to generate extra questions..")
	load_dotenv(dotenv_path="../../../.env")
	client = genai.Client(api_key=os.environ["LLM_API_KEY"])
	data = generate(client, "gemini-3.1-flash-lite", prompt)
	with open("GENERATED_QUESTIONS.json", "w", encoding="utf-8") as file:
		json.dump(data, file, indent=2)
	print(data)
	return data

# remove gemini as a magic number, have it defined in .env
# create a fake lobby filled with questions, answers and categories in order to inject into this function for testing
# think about how emulate it, perhaps you need to populate the database with a lobby
# call POST from SWAGGER while using this emulated lobby
