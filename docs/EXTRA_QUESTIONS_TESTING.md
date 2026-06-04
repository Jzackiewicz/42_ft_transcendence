# Testing Extra Question Generation

Use this single automated flow to test all three cases A, B, and C.

1. Start the dev stack, apply migrations, and seed base questions:
```bash
make dev-up
make dev-migrate
make dev-seed
```

2. Run the integration test that mocks the LLM and verifies the whole flow:
```bash
make dev-test TEST=game.tests.test_generate_extra_questions_integration
```

What this one test covers
- A: it POSTs the lobby UUID and question count to `/game/generate_extra_questions/` and expects a 200 response.
- B: it checks that the database gained `Question` rows with `is_ai_generated=True`.
- C: it checks that the requesting `GameSession` gained new `SessionQuestion` rows for the generated questions.

That is the only supported test path in this guide. The test is fully automated and does not require a real `LLM_API_KEY` because the LLM call is mocked.

3. Run the REST API tests:
```bash
make dev-test TEST=game.tests.test_generate_extra_questions_api
```

What these tests cover
- 1: test_generate_extra_questions_success
	- Host successfully generates questions and receives a 200 OK.
- 2: test_generate_extra_questions_rejects_more_than_50
	- Requesting more than 50 questions returns 400 Bad Request.
- 3: test_generate_extra_questions_uses_default_amount
	- If no amount is provided, the API uses the default of 10 questions.
- 4: test_generate_extra_questions_rejects_non_host
	- A non-host user cannot generate questions and receives 400 Bad Request.
- 5: test_generate_extra_questions_missing_room_returns_404
	- An invalid/nonexistent session UUID returns 404 Not Found.
- 6: test_generate_extra_questions_rejects_started_room
	- Question generation is rejected if the game has already started (not in lobby state).
- 7: test_generate_extra_questions_is_limited_per_user_per_hour
	- After 5 successful requests within an hour, the 6th request is blocked with 429 Too Many Requests.