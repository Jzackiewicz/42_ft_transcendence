"""Question generation utilities backed by the Google GenAI SDK."""

from __future__ import annotations

import json
import os
import time
from typing import Any


DEFAULT_MODEL = "gemini-3.1-flash-lite-preview"
DEFAULT_RESPONSE_MIME_TYPE = "application/json"

SYSTEM_INSTRUCTION = """You must respond using JSON only.
Return a JSON object with a "questions" array.
Each item in the array must contain "category", "question", and "answer" fields.
The "answer" field must be an array of possible answers to the question.
The "question" field must be a string containing the question itself.
Questions must give a clear indication of what the answer should be, and the answer must be a clear and concise response to the question.
Answers must be made up of only one word, short phrase, or name each.
Questions must not include the words "and", "type", or "while".
Questions must give the full context of the question and must not rely on the category field to provide context.
If a question can have multiple answers, create a very extensive list of answers for that question.
If an answer can have nicknames, include both the nickname and the actual name.
Generate an appropriate category name for each question that is relevant to the question and answer.
The category name must be a single word or phrase and must not be a generic term like "general" or "miscellaneous".
If you are not 100% sure about an answer, do not include it."""


def _get_client():
	from google import genai

	api_key = os.getenv("SECURE_AI_API_KEY")
	if not api_key:
		raise RuntimeError("Missing SECURE_AI_API_KEY environment variable")

	return genai.Client(api_key=api_key)


def _normalize_generated_payload(data: Any, *, category: str, question_count: int) -> dict[str, Any]:
	if isinstance(data, dict):
		questions = data.get("questions")
		if isinstance(questions, list):
			return {
				"requested_category": category,
				"question_count": question_count,
				"questions": questions,
			}

		if {"category", "question", "answer"}.issubset(data.keys()):
			return {
				"requested_category": category,
				"question_count": question_count,
				"questions": [data],
			}

	if isinstance(data, list):
		return {
			"requested_category": category,
			"question_count": question_count,
			"questions": data,
		}

	raise ValueError("AI response must be a JSON object or array")


def generate_questions(*, category: str, question_count: int, model: str = DEFAULT_MODEL) -> dict[str, Any]:
	if question_count < 1:
		raise ValueError("question_count must be greater than zero")

	client = _get_client()
	prompt = f"Generate {question_count} questions and answers based off of {category}."

	for attempt in range(5):
		try:
			response = client.models.generate_content(
				model=model,
				contents=prompt,
				config={
					"system_instruction": SYSTEM_INSTRUCTION,
					"response_mime_type": DEFAULT_RESPONSE_MIME_TYPE,
				},
			)
			data = json.loads(response.text)
			return _normalize_generated_payload(
				data,
				category=category,
				question_count=question_count,
			)
		except Exception as exc:
			if "503" in str(exc) and attempt < 4:
				time.sleep(2)
				continue
			raise

	raise RuntimeError("AI servers are too busy")


def main() -> None:
	from dotenv import load_dotenv

	import sys

	if len(sys.argv) != 2 or sys.argv[1] != "arm":
		print('If you wish to call the API, run the program with the argument "arm".')
		raise SystemExit(1)

	print("Setting up..")
	load_dotenv(dotenv_path="../.env")
	data = generate_questions(category="History", question_count=80)
	with open("output.json", "w", encoding="utf-8") as file:
		json.dump(data, file, indent=2)
	print(data)


if __name__ == "__main__":
	main()
