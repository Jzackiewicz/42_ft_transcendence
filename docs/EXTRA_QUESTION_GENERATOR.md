# Extra Question Generator

This document describes the current extra-question flow used by the lobby host endpoint and the support module in `server/game/services/extra_question_generator.py`.

## Purpose

The feature generates additional question data for a game lobby by sending the lobby’s existing questions to the Google GenAI API. The generated output is written to `GENERATED_QUESTIONS.json` for inspection and manual testing.

## HTTP Endpoint

- `POST /api/game/generate_extra_questions/`
- Host-only lobby action
- Request body:

```json
{
  "session_uuid": "123e4567-e89b-12d3-a456-426614174000",
  "n_questions_to_generate": 10
}
```

`n_questions_to_generate` is optional and defaults to `10`.

## Files Involved

- `server/game/apis.py`
- `server/game/serializers.py`
- `server/game/urls.py`
- `server/game/services/lobby/lobby_management.py`
- `server/game/services/lobby/guards.py`
- `server/game/services/extra_question_generator.py`
- `server/game/services/extra_question_generator_system_instruction.txt`
- `server/requirements.txt`

## Current Flow

1. The API receives `session_uuid` and optional `n_questions_to_generate`.
2. The lobby service checks that the caller is authenticated, belongs to the lobby host, and that the room is still in `lobby` state.
3. `generate_extra_questions_for_room()` resolves the lobby and delegates to `generate_extra_questions()`.
4. `generate_extra_questions()` loads source questions through `load_lobby_questions()`.
5. The source questions are serialized into a prompt string.
6. The module loads the system instruction from `extra_question_generator_system_instruction.txt` at import time.
7. `generate()` calls `client.models.generate_content(...)` with:
   - the prompt as `contents`
   - the loaded system instruction as `system_instruction`
   - `application/json` as the response MIME type
8. The response text is parsed with `json.loads()`.
9. The parsed data is written to `GENERATED_QUESTIONS.json`.

## Dependency Notes

The backend now depends on the Google GenAI SDK.

- `server/requirements.txt` includes `google-genai==2.7.0`
- The module imports it as `from google import genai`
- The API key is read from `LLM_API_KEY`

## System Instruction Location

The instruction block lives in a plain text file next to the module:

- `server/game/services/extra_question_generator_system_instruction.txt`

This keeps the prompt text easy to edit without touching the Python logic.

## Error Handling Convention

The current pattern is:

- retry on `503` responses up to 5 attempts
- print a message while retrying
- raise a `RuntimeError` for fatal failures
- raise a `RuntimeError` again if all retries are exhausted

This matches the project’s general service-layer style, where business logic and external failure conditions are surfaced with Python exceptions rather than `sys.exit()`.

## Notes on Project Convention

The rest of the backend follows a similar pattern:

- `ValidationError` is used for domain or access failures in service helpers
- serializer validation uses DRF serializers
- `RuntimeError` is used for runtime/config/external-service failures
- `SystemExit` is reserved for command-line entrypoints

## Manual Test Hook

The module can still be run manually for local testing.

```python
# generate_extra_questions(1, 30)
```

Uncommenting it and running the file directly will generate a `GENERATED_QUESTIONS.json` file.

## Current Caveats

- `load_dotenv()` currently uses a relative `.env` path in the module.
- `GENERATED_QUESTIONS.json` is written to the current working directory.
- There are still no automated tests for the model retry behavior or JSON parsing failures.

## Future Cleanup Ideas

- Resolve the `.env` and output paths from the module directory.
- Move `GENERATED_QUESTIONS.json` output to a clearly defined test or debug location.
- Add automated tests for retry behavior and JSON parsing failures.
- Replace the lobby question source with a dedicated generation workflow once that path is finalized.
