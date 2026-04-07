# Project Single Source of Truth: Quizscendence

## 1. Project Vision (Elevator Pitch)
Quizscendence is a real-time multiplayer browser game, inspired by the classic Polish TV game show "1 z 10" (1 out of 10).  This project is developed as part of the `ft_transcendence` module at School 42. The core innovation is the use of a Large Language Model (LLM) acting as an AI Judge, which evaluates the correctness of players' text-based answers in real-time.

## 2. Architecture & Tech Stack
The project relies on a strict frontend-backend separation with a strong emphasis on real-time bidirectional communication.

* **Frontend:** React.js (Single Page Application).
* **Backend:** Django (Python).
    * *Django REST Framework (DRF)* - Handles standard HTTP requests (auth, profiles).
    * *Django Channels* - Handles WebSockets (core game engine).
* **Databases:**
    * *PostgreSQL* - Primary relational DB (users, stats, match history, question pool).
    * *Redis* - In-Memory DB / Message Broker (WebSocket layer, fast game state).
* **AI Integration:** LLM Interface (e.g., OpenAI / Gemini API) used purely as the validation engine.
* **DevOps:** Docker (docker-compose, Dockerfiles), Makefile - fully containerized environment.

## 3. Project Scope

### Phase 1: Absolute MVP (Critical for Defense)
* **User Module:** Registration, login (JWT), profile management (avatar, win/loss stats).
* **Social Module:** Friends system (add/remove), online status tracking.
* **Lobby & Matchmaking:** Ability to create/join game rooms.
* **Game Engine (WebSockets):** * Broadcasting questions to players.
    * Receiving text-based answers.
    * Forwarding answers to the AI Judge for evaluation.
    * Broadcasting the verdict and updating turn/score state.

### Phase 2: Nice-to-Have (Time Permitting)
* Progressive Web App (PWA) for mobile support.
* Full Public API (external access to stats).
* AI Opponent (bots filling empty slots in a room).
* Voice Integration (answering via microphone instead of keyboard).
* ML Recommendations.
* Spectator mode.

## 4. Game Mechanics & Flow

* **Room Size:** Flexible. A game can start with anywhere from **2 to 10 players**.
* **Question Pool:** Questions are fetched from a pre-populated PostgreSQL database containing 200 questions along with their canonical answers.
* **UI/UX Design:** Minimalist and clean. Focused on high readability and ease of implementation over complex animations.

### Game Rules / Elimination [PENDING DECISION]
The team must decide between two game modes before implementing the final game loop:
* **Option A (Classic TV Show):** Three distinct rounds. Players have a set number of "lives/chances". A wrong answer loses a life. Losing all lives means elimination. Players nominate each other to answer.
* **Option B (Points-Based Sprint):** A single, continuous round. Every player answers every question simultaneously (or in quick succession). No lives/eliminations. The player with the most points after a set number of questions wins.

### The AI Judge Mechanic
1. Player types their answer.
2. Server locks the game state for others.
3. Server securely sends a prompt to the LLM: *"The question is X. The correct database answer is Y. The player said Z. Is this acceptable? Answer TRUE or FALSE."*
4. The server receives the boolean verdict and applies game logic (deducts life or awards points).

## 5. Data Flow
* **HTTP/REST:** Used **only** outside of the active game (login, fetching match history, updating account settings, browsing the lobby).
* **WebSockets:** Used from the moment players enter the game room. Responsible for live events such as: `new_question`, `player_answered`, `ai_verdict`, `turn_changed`, `game_over`.