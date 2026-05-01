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
	- **core/** - main project directory, settings, routings, ASGI/WSGI configuration etc.

- ***applications***
	- **account/** - setting up an account, logging, registering, authentication etc.
	- **social/** - chat, friends system
	- **game/** - game domain logic


>The sections range might change later in the development (I hope not though)

### Service layer pattern
We're using [this styleguide](https://github.com/HackSoftware/Django-Styleguide) meaning mostly splitting business logic from interface (sending requests).

It means our code structure looks like this:
- `selectors.py` - read/query logic, used for fetching and preparing data.
- `services.py` - business logic and state-changing use-cases.
- `apis.py` - HTTP interface layer.
- `consumers.py` - WebSocket interface layer.
- `serializers.py` - input/output validation and serialization.
- `models.py` - database schema and ORM relations.
- `urls.py` / `routing.py` - HTTP and WebSocket routing.

### Game section
#### Game logic

Base game loop is constructed as a finite state machine (FSM) visualized as a graph below:

![FSM_diagram](game_state_machine.svg)

States:

- `Lobby` - waiting for players and game start.
- `Answering` - current player answers a question.
- `Evaluation` - answer is evaluated as correct, wrong or timeout.
- `Nomination` - last correct player selects the next player.
- `GameOver` - game is finished.

#### Game loop rules
Whole game loop is fully backend-driven, frontend only sends player actions and renders the snapshots returned by the backend.

Current architecture:
- `fsm.py` - declared states and trasition with no business logic
- `services/` - business logic including game rules, calling FSM transitions, calling ORM data models
- `selectors.py` - game state snapshots ***(TBA)***
- `consumers.py` - Websocket interface layer ***(TBA)***

#### Game Data model (ORM)
![EntityRelationDiagram](game_erd.svg)
*Where `User` entity is a placeholder for actual entity of registered user `AUTH_USER_MODEL`*.

*Diagrams generated with*
```bash
python -m statemachine.contrib.diagram game.fsm.GameStateMachine game_fsm.png
python manage.py graph_models game --pydot -g -o game_erd.svg   
```
### Endpoints

- `http://127.0.0.1:8000/api/docs/` - HTTP endpoints documentation (+ manual testing)
- `docs/WEBSOCKET_EVENTS.md` - websocket endpoints documentation


		To test websocket endpoints manually you need to use wscat or install Postman

- To run automatic tests run the following command: 
	```bash
	make dev-test
	```
## Frontend
¯\\_( ͡° ͜ʖ ͡°)_/¯