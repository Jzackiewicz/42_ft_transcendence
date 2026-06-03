# Extra Question Generator

This is the lobby-host flow that generates more questions from the lobby’s current question set.

## Endpoint

`POST /api/game/generate_extra_questions/`

Request body:

```json
{
  "session_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "n_questions_to_generate": 10
}
```

`n_questions_to_generate` defaults to `10`.

## What It Does (Simplified)

- Validates the caller is the lobby host and the game is still in the lobby state.
- Reads the lobby's existing `SessionQuestion`s (question text, correct answer, category) and builds a JSON prompt.
- Calls the LLM (via `google-genai`) to generate new question objects.
- Normalizes the LLM JSON into a list of question dicts and filters/validates fields.
- For each generated item, creates or updates a `Question` row with `is_ai_generated=True`.
- Attaches each new `Question` to the `GameSession` by creating `SessionQuestion` rows (preserving order).
- Returns a JSON response containing the new `Question` ids so the client can fetch or display them.

## Key Files

- `server/game/apis.py`
- `server/game/services/lobby/lobby_management.py`
- `server/game/services/extra_question_generator.py`
- `server/game/services/extra_question_generator_system_instruction.txt`

## Notes

- The backend uses `google-genai` and `LLM_API_KEY`.
- The generator retries `503` responses and raises `RuntimeError` for fatal failures.
- The supported automated test for this flow is `game.tests.test_generate_extra_questions_integration`.

## Response

- Success (HTTP 200):

```json
{ "created_question_ids": [123, 124, 125] }
```

- Validation error → HTTP 400 with `{"error": [...]}.
- Room not found → HTTP 404 with `{"error": "Room not found"}`.
- LLM/generation failure → HTTP 502 with `{"error": "<message>"}`.
