# Project Progress: Issue #13 - Docker Infrastructure

## Accomplishments

### 1. Project Scaffolding

- **Frontend**: Created `client/` directory with a dummy React + Vite + TypeScript setup.
- **Backend**: Verified `server/` readiness and integrated it with the container environment.
- **Secrets**: Initialized `devops/secrets/` with mandatory `.txt` files for sensitive data, moving away from plain `.env` for production-grade security.

### 2. Containerization (Dockerfiles)

- **Django (`api`)**:
  - Base: `python:3.13.1-slim` (we are able to change it later)
  - Features: Automatic DB wait loop, migration execution, and `collectstatic`.
  - Server: `Daphne` for ASGI/WebSocket support.
- **React (`web`)**:
  - Build Stage: `node:20.12.2-alpine3.19` using `npm install`.
  - Production Stage: `nginx:1.25.5-alpine3.19` serving static assets from `dist/`.
- **Proxy (`proxy`)**:
  - Base: `nginx:1.25.5-alpine3.19`.
  - Security: Force HTTPS redirect, self-signed SSL cert generation for local dev.
  - Routing: Unified entry point for Frontend (`/`), API (`/api/`), Admin (`/admin/`), and WebSockets (`/ws/`).

### 3. Orchestration (`docker-compose.yml`)

- **Services**: `db` (Postgres 15), `redis` (v7), `api`, `web`, `proxy`.
- **Networking**: Isolated `frontend` and `backend` bridges.
- **Secrets**: Native Docker secrets mounted at `/run/secrets/` for `DB_PASSWORD`, `DJANGO_SECRET_KEY`, and `LLM_API_KEY`.
- **Volumes**: Persistent storage for Postgres data, Django media (avatars), and shared static files.

### 4. Automation & Documentation

- **Makefile Commands**:
  - `make up`: Build and start stack detached.
  - `make down`: Stop stack.
  - `make restart`: restart.
  - `make logs`: Follow container output.
  - `make ps`: Status check.
  - `make clean`: Stop and wipe volumes (reset DB).
  - `make fclean`: Stop and wipe volumes (reset DB), docker prune.
  - `make re`: fclean and rebuild.
  - `make createsuperuser`: Easy admin creation for Django.
  > [!IMPORTANT]
  > added action confirmation before full wipe with clean/fclean and re for data persitance reasons
- **Documentation**: Added comprehensive links to official docs (Docker, Nginx, Django, Node) in all infrastructure files for maintainability (as it is easy to forget all the configs)

## Troubleshooting & Key Fixes

- **Build Context**: Adjusted `docker-compose.yml` to use `context: ..` so Dockerfiles in `devops/` can access source code in root subdirectories.
- **Secret Formatting**: Fixed `OperationalError` by removing comments from `.txt` secret files (Postgres/Django read raw file content).
- **Django Settings**:
  - Implemented `get_secret()` helper in `settings.py` to bridge Docker secrets and environment variables.
  - Configured `STATIC_ROOT` to fix `ImproperlyConfigured` error during container startup.
  - Added `CSRF_TRUSTED_ORIGINS` and `SECURE_PROXY_SSL_HEADER` to fix **Forbidden (403)** error when logging into admin panel.
- **Nginx Routing**: Added missing proxy rules for `/account/` and `/game/` to fix **404 Not Found** errors on backend endpoints.

## Testing Endpoints

- **Frontend**: `https://localhost/`
- **Django Admin**: `https://localhost/admin/`
- **API Docs**: `https://localhost/api/docs/`
- **Account API**: `https://localhost/account/users/`
- **Game API**: `https://localhost/game/questions/`

## Persistent uncertainties

- in react dockerfile, not sure if to expose 443, 80 or both
- react might change to next.js with the container requiring adjustments
