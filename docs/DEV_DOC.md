# DEV DOCUMENTATION
For making our lives easier

## Backend

### Installing & running
	You need to have python 3.11+ installed

To run the server:
```bash
chmod +x dev.sh
./dev.sh
```

### Codebase
Server is split into sections:

- ***main project***
	- **core/** - main project directory, settings, routings etc.

- ***applications***
	- **account/** - stuff related to setting up an account, logging, registering, authentication etc. *(HTTP requests mostly)*
	- **social/** - chat, friends system *(HTTP + websockets)*
	- **game/** - game logic *(ws mostly)*


>The sections range might change later in the developement (I hope not though)

### Service layer pattern
We're using [this styleguide](https://github.com/HackSoftware/Django-Styleguide) meaning mostly splitting business logic from interface (sending requests).

It means our code structure looks like this:
- `selectors.py` (for reading endpoints) and `services.py` (for creating/editing/deleting endpoints) - storing HTTP endpoints logic
- `apis.py` (for HTTP) and `consumers.py` (for ws) - handling interface
- `serializers.py` - validation schemes
- `models.py` - database tables structure (for ORM)
- `urls.py` (HTTP) and `routing.py` (ws) - url routing 

### Game section
#### Game logic

Base game loop is constructed as a finite state machine (FSM) visualized as a graph below:

![FSM_diagram](game_state_machine.png)
,where:

- `Lobby` – waiting for players and game start
- `Answering` – current player answers a question
- `Evaluation` – answer is evaluated (correct / wrong / timeout)
- `Nomination` – last correct player selects next player
- `GameOver` – game finished


#### Game Data model (ORM)
```mermaid
erDiagram

    GameSession {
        int id
        uuid session_uuid
        string current_status
        int current_player_id
        int last_correct_player_id
        int last_nominated_player_id
        int current_question_id
        int winner_id
        string end_reason
        int question_asked_count
        datetime created_at
        datetime started_at
        datetime ended_at
    }

    SessionPlayer {
        int id
        int session_id
        int user_id
        string player_type
        string display_name
        int seat_number
        int lives
        int points
        int answered_count
        int total_answer_time_ms
    }

    User {
        int id
    }

    Question {
        int id
        string question_text
        string correct_answer
    }

    SessionQuestion {
        int id
        int session_id
        int question_id
        int order_index
    }

    AnswerAttempt {
        int id
        int session_id
        int player_id
        int session_question_id
        string answer_text
        bool is_timeout
        bool is_correct
        string evaluation_status
        int answer_time_ms
        datetime created_at
        datetime evaluated_at
    }

    GameSession ||--o{ SessionPlayer : has_players
    GameSession ||--o{ SessionQuestion : has_questions
    GameSession ||--o{ AnswerAttempt : has_attempts

    User o|--o{ SessionPlayer : participates_as_human

    Question ||--o{ SessionQuestion : used_in_session

    SessionPlayer ||--o{ AnswerAttempt : makes
    SessionQuestion ||--o{ AnswerAttempt : answered_in

    SessionPlayer o|--o{ GameSession : current_player
    SessionPlayer o|--o{ GameSession : last_correct_player
    SessionPlayer o|--o{ GameSession : last_nominated_player
    SessionPlayer o|--o{ GameSession : winner

    SessionQuestion o|--o{ GameSession : current_question
```
*Where `User` entity is a placeholder for actual entity of registered user (TBA)*.


### Endpoints

- `http://127.0.0.1:8000/api/docs/` - HTTP endpoints documentation (+ manual testing)
- `docs/WEBSOCKET_EVENTS.md` - websocket endpoints documentation


		To test websocket endpoints manually you need to use wscat or install Postman

- To run automatic tests run the following command: 
	```bash
	python3 manage.py test
	```
## Frontend
¯\\_( ͡° ͜ʖ ͡°)_/¯