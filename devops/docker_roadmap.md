# Roadmap: Issue #13 - Docker Infrastructure

## 1. Project Scaffolding
- **Frontend**: Create `client/` directory for React app.
- **Backend**: Ensure `server/` is ready for containerization.
- **Secrets Management**: 
  - Create `devops/secrets/` directory.
  - Define separate files for sensitive data: `db_password.txt`, `django_secret_key.txt`, `llm_api_key.txt`.
  - Use `.env` only for non-sensitive config (e.g., `DEBUG=True`, `DB_NAME=quizdb`).

## 2. Build Dockerfiles
... (rest of Build Dockerfiles) ...

## 3. Orchestrate Stack (`docker-compose.yml`)
- Define top-level `secrets` block pointing to `devops/secrets/` files.
- Define services:
  - `db`: PostgreSQL 15 image.
    - **Secrets**: `POSTGRES_PASSWORD_FILE` pointing to `/run/secrets/db_password`.
    - **Persistence**: `postgres_data` volume.
  - `redis`: Redis 7 image (Channel Layer).
  - `api`: Django container.
    - **Secrets**: Access to all relevant files in `/run/secrets/`.
    - **Persistence**: `media_data` volume for avatars.
  - `web`: React container.
  - `proxy`: NGINX container (depends on `api`, `web`).
- Network: Isolated `backend` and `frontend` networks.


## 4. Automation & Cleanup

- Create `Makefile`:
  - `up`: `docker-compose up -d --build`
  - `down`: `docker-compose down -v`
  - `re`: `down up`
  - `clean`: Remove unused images/volumes.
- Remove deprecated `dev.sh` (if exists).
- Update `SETUP.md` with Docker instructions.
