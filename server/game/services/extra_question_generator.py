import json
import os
from pathlib import Path
from dotenv import load_dotenv
from google import genai
import time

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
	"""Takes a lobby ID and returns a a data object containing the questions, their answers, and a category for each question."""
	# TODO actually load the lobby_id and take the needed data from the database.
	# For now we just load a json file with dummy data to test the generate_expanded_questions function.

	with open("../tests/dummy_questions.json", "r") as f:
		questions_data = json.load(f)
	return questions_data

# TODO Update the load_lobby_questions function to actually load data from a lobbies questions once one exists with seeded data.
# This function can raise an exception
def generate_extra_questions(lobby_id, n_questions_to_generate):
	"""Takes a lobby ID and generates json formatted questions based the lobbies questions."""
	questions_data = load_lobby_questions(lobby_id)

	prompt = "Generate " + str(n_questions_to_generate) + " questions and answers based off of the following questions: " + json.dumps(questions_data) + ". The questions must not be duplicates of the ones given."
	print("About to generate extra questions..")
	load_dotenv(dotenv_path="../../../.env")
	client = genai.Client(api_key=os.environ["LLM_API_KEY"])
	# IF MODEL IS NOT CORRECT CHANGE THE CLIENT TO ONE PRINTED IN THE CODE BELOW
	# models = client.models.list()
	# for model in models:
	# 	print(model.name)
	# return
	data = generate(client, "gemini-3.1-flash-lite", prompt)
	with open("GENERATED_QUESTIONS.json", "w", encoding="utf-8") as file:
		json.dump(data, file, indent=2)
	print(data)
	return data

# to test generate extra questions, uncomment the line below and run "python3 extra_question_generator.py". It will make a GENERATED_QUESTIONS.json with all the extra questions for demo purposes only.
# generate_extra_questions(1, 30) 

