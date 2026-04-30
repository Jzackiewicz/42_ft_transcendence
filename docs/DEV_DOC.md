# DEV DOCUMENTATION

For making our lives easier

## Backend

### Installing & running

You need to have python 3.11+ installed.

> [!IMPORTANT]
> First: create .env based on .env.example

To run the server for the first time (sets up isolated dev database):

```bash
make dev-up       # Start DB and Redis
make dev-migrate  # Run migrations
make dev-runserver # Start Django
```

To run production setup:

> [!IMPORTANT]
> If the default setup does not work it might be because default port is blocked
> on campus workstation, read the error and change the port in .env in neccesary

```bash
make up
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

### Endpoints

| Page | Production (HTTPS) | Local Dev (HTTP) |
| --- | --- | --- |
| Admin panel | <https://localhost:8443/admin/> | <http://127.0.0.1:8000/admin/> |
| API docs (Swagger) | <https://localhost:8443/api/docs/> | <http://127.0.0.1:8000/api/docs/> |
| Questions API | <https://localhost:8443/game/questions/> | <http://127.0.0.1:8000/game/questions/> |
| Users API | <https://localhost:8443/account/users/> | <http://127.0.0.1:8000/account/users/> |
| WebSocket docs | `docs/WEBSOCKET_EVENTS.md` | - |

- To run automatic tests:

 ```bash
 make dev-test
 ```

- To manage local admin accounts:

 ```bash
 make dev-createsuperuser
 ```

- To open a local Django shell:

 ```bash
 make dev-shell
 ```

- To test websocket endpoints manually you need to use wscat or install Postman

## Frontend

¯\\*( ͡° ͜ʖ ͡°)*/¯

## DevOps

### Infrastructure Strategy

- **Isolation**: Production (`prod-transcendence`) and Local Dev (`dev-transcendence`) use separate Docker volumes and project names to prevent data collision.
- **Port Mapping**: Host ports `80` and `443` are blocked. We use `8080` (HTTP) and `8443` (HTTPS) for production. Dev stack uses `5433` (DB) and `6380` (Redis) on host.
- **Security**: Nginx handles SSL termination and redirects all HTTP traffic to HTTPS.

### Redis usage

Redis acts as the backing store for **Django Channels (`CHANNEL_LAYERS`)**.

- **Why**: WebSockets require shared state between different processes (e.g., Daphne serving the socket and a background worker sending a message).
- **Where**: Used in `social/` (chat) and `game/` (real-time updates).
- **Configuration**: Set in `server/core/settings.py`. Uses `redis://redis:6379` in production containers and `redis://127.0.0.1:6380` for local development via `Makefile` overrides.

### Containers

- **api**: Django/Daphne (Python 3.13)
- **web**: React (Nginx serving static files)
- **proxy**: Nginx (Unified entry point + SSL)
- **db**: PostgreSQL 15
- **redis**: Redis 7
