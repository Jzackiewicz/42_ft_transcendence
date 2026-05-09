# Project Single Source of Truth: Quizscendence

## 1. Project Vision (Elevator Pitch)
Quizscendence is a real-time multiplayer browser quiz game inspired by the Polish TV game show "1 z 10" ("1 out of 10").

The game is played by maximum of 5 players in a shared lobby. Players answer text-based questions, lose lives after wrong answers or timeouts, gain points for correct answers, and nominate other players after answering correctly.

The backend is the source of truth for the whole game flow. The frontend only sends player actions and renders the state returned by the backend.

Answer correctness is currently based on canonical answers stored in the database.

Game supports additional features like optional question generation with AI and AI-controlled bot players.

This project is developed as part of the `ft_transcendence` module at School 42.

## 2. Architecture & Tech Stack

The project relies on a strict frontend-backend separation with a strong emphasis on real-time bidirectional communication.

* **Frontend:** React.js (Single Page Application).
* **Backend:** Django (Python).
  * *Django REST Framework (DRF)* - Handles standard HTTP requests (auth, profiles).
  * *Django Channels* - Handles WebSockets (core game engine).
* **Databases:**
  * *PostgreSQL* - Primary relational DB (users, stats, match history, question pool).
  * *Redis* - In-Memory DB / Message Broker (WebSocket layer, fast game state).
* **AI Integration:** external LLM calls for generating questions, simulating bots moves.
* **DevOps:** Docker (docker-compose, Dockerfiles), Makefile - fully containerized environment.

## 3. Project Scope

### User Management

- User registration.
- Login/logout.
- Secure authentication.
- Profile management.
- Avatar support.
- Basic user statistics.

### Social Features

- Friends system.
- Online status.
- Basic chat or user interaction features.

### Lobby

- Create or join a game lobby.
- Each lobby must contain a maximum of 5 players.
- A game requires a minimum of 2 players to start.
- A player slot may be occupied by a human player or an AI bot.
- Lobby settings define the game configuration before the game starts.

### Game Flow

- Real-time multiplayer quiz game.
- Backend-driven finite state machine.
- Text-based answers.
- Answer timeout support.
- Lives, points, nomination and fallback rules.
- Game-over resolution and winner selection.
- WebSocket-based state updates.

### Questions

- Questions are stored in the database.
- Each question has:
  - question text,
  - canonical correct answer,
  - category.
- Session questions are assigned to a specific game session with deterministic order.
- AI may optionally generate additional questions before the game starts.

### AI Bots

- Bot players may fill player slots.
- Bots must use the same game flow as human players.
- Bot actions must go through the same backend game action path as human actions.
- Bots must not directly modify game state.

### DevOps

- Dockerized project.
- Single-command startup.
- `.env` for local secrets.
- `.env.example` for required environment variables.
- No credentials committed to Git.

## 4. Game Rules & Flow

### Lobby Size

- A game lobby can contain up to 5 players.
- A player slot may be occupied by either a human player or an AI bot.
- Bot players may be used to fill empty slots.

### Starting the Game

- The game starts from the `Lobby` state.
- The first answering player is selected randomly from alive players.
- The backend assigns the first question.
- After the game starts, the session enters the `Answering` state.
- Entering `Answering` creates an active `AnswerAttempt`.

### Lives

- Each player starts with a configured number of lives.
- Default value: 3 lives.
- Wrong answer removes 1 life.
- Timeout removes 1 life.
- A player with 0 lives is eliminated.
- Eliminated players cannot be nominated or answer questions.

### Answering

- Only `current_player` can submit an answer.
- Each answering turn has:
  - `current_player`,
  - `current_question`,
  - `current_attempt`.
- The backend stores the submitted answer.
- If the answer timeout is exceeded ***(To be changed later)***:
  - the attempt is marked as timeout,
  - submitted answer text is ignored,
  - the answer is treated as wrong.

### Answer Evaluation

- Answer correctness is decided by the backend.
- Current implementation uses canonical answer matching ***(To be changed later)***:

```text
normalized(player_answer) == normalized(question.correct_answer)
```

### Scoring

- Correct answer gives **10 points**.
- Correct answer by the **nominated player** gives **20 points**.
- Wrong answer gives **0 points**.
- Timeout gives **0 points**.
- Each evaluated attempt increments `answered_count`.
- Answer time is accumulated in `total_answer_time_ms`.

### Nomination

- A player who answers correctly becomes `last_correct_player`.
- `last_correct_player` receives the right to nominate the next answering player.
- Only `last_correct_player` can nominate.
- The nominated player becomes `current_player`.
- A dead player cannot be nominated.

### Wrong Answer and Nomination Rights

- Wrong answer or timeout does **not** clear `last_correct_player`.
- Nomination rights stay with `last_correct_player` as long as they are alive.
- If a nominated player answers incorrectly, the previous `last_correct_player` can nominate again.
- Nomination rights change only when:
  - another player answers correctly, or
  - the current `last_correct_player` is no longer alive.

### Game Over

The game ends when:

- only one player is alive
or
- all session questions have been used.

	- If all questions are exhausted, the winner is selected by tie-breakers:
		1. points DESC
		2. answered_count DESC
		3. total_answer_time_ms ASC
		4. seat_number ASC