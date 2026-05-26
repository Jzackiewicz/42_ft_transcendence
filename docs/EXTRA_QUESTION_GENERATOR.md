# Extra Question Generator

This document describes the current state of `server/game/services/extra_question_generator.py` and the small support file it depends on.

## Purpose

The module generates additional question data for a game lobby by sending existing lobby questions to the Google GenAI API. The generated output is written to `GENERATED_QUESTIONS.json` for inspection and manual testing.

## Files Involved

- `server/game/services/extra_question_generator.py`
- `server/game/services/extra_question_generator_system_instruction.txt`
- `server/game/tests/dummy_questions.json`

## Current Flow

1. `generate_extra_questions(lobby_id, n_questions_to_generate)` loads source questions through `load_lobby_questions()`.
2. The source questions are serialized into a prompt string.
3. The module loads the system instruction from `extra_question_generator_system_instruction.txt` at import time.
4. `generate()` calls `client.models.generate_content(...)` with:
   - the prompt as `contents`
   - the loaded system instruction as `system_instruction`
   - `application/json` as the response MIME type
5. The response text is parsed with `json.loads()`.
6. The parsed data is written to `GENERATED_QUESTIONS.json`.

## System Instruction Location

The instruction block is no longer embedded inside `generate_extra_questions()`. It now lives in a plain text file next to the module:

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

- `ValueError` is commonly used for domain or validation failures in service helpers
- `serializers.ValidationError` is used in serializer validation
- `RuntimeError` is used for runtime/config/external-service failures
- `SystemExit` is reserved for command-line entrypoints

## Manual Test Hook

The module includes a commented-out call at the bottom for local testing:

```python
# generate_extra_questions(1, 30)
```

Uncommenting it and running the file directly will generate a `GENERATED_QUESTIONS.json` file.

## Future Cleanup Ideas

- Replace the hard-coded relative paths with paths resolved from the module directory.
- Move `GENERATED_QUESTIONS.json` output to a clearly defined test or debug location.
- Add automated tests for retry behavior and JSON parsing failures.
- Replace the dummy loader with the real lobby/question data source when that path is available.
