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
