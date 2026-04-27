# Docker Infrastructure

## Accomplishments

### 1. Project Scaffolding

- **Frontend**: Created `client/` directory with a dummy React + Vite + TypeScript setup.
- **Backend**: Verified `server/` readiness and integrated it with the container environment.
- **Configuration**: Migrated from individual Docker secret files to a unified `.env` at the root for easier local development and management.

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
- **Environment**: Unified `.env` file loaded via `env_file` directive for all relevant services.
- **Volumes**: Persistent storage for Postgres data, Django media (avatars), and shared static files.

### 4. Local Development Environment

- **Isolation**: Implemented dedicated development stack using Docker project name `dev-transcendence` to isolate volumes and containers from production.
- **Port Management**: Configured variable-based host port mapping to avoid collisions. Dev stack uses `5433` (DB) and `6380` (Redis).
- **Makefile Automation**:
  - `make dev-deps`: Start isolated DB and Redis.
  - `make dev-migrate`: Run Django migrations against dev DB.
  - `make dev-runserver`: Start Django locally with dev environment overrides.
  - `make dev-test`: Execute tests against isolated dev stack.
  - `make dev-createsuperuser`: Manage local admin accounts.
  - `make dev-down` / `make dev-clean`: Stop or wipe dev environment without affecting production data.

### 5. Automation & Documentation

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
  > added action confirmation before full wipe with clean/fclean and re for data persistence reasons
- **Documentation**: Added comprehensive links to official docs (Docker, Nginx, Django, Node) in all infrastructure files for maintainability (as it is easy to forget all the configs)

## Troubleshooting & Key Fixes

- **Django Settings**:
  - Configured `STATIC_ROOT` to fix `ImproperlyConfigured` error during container startup.
  - Added `CSRF_TRUSTED_ORIGINS` and `SECURE_PROXY_SSL_HEADER` to fix **Forbidden (403)** error when logging into admin panel.
- **Nginx Routing**:
  - changed port mapping from `80` to `8080` and from `443` to `8443`

## Testing Endpoints

- **Frontend**: `https://localhost:8443/`
- **Django Admin**: `https://localhost:8443/admin/`
- **API Docs**: `https://localhost:8443/api/docs/`
- **Account API**: `https://localhost:8443/account/users/`
- **Game API**: `https://localhost:8443/game/questions/`

## Persistent uncertainties

- in react dockerfile, not sure if to expose 443, 80 or both
- react might change to next.js with the container requiring adjustments
