# https://www.gnu.org/software/make/manual/make.html

NAME = transcendence

DOCKER_COMPOSE = docker compose
DOCKER_COMPOSE_FILE = ./devops/docker-compose.yml
PROD_PROJECT = prod-transcendence
DEV_PROJECT = dev-transcendence

# Load environment variables from .env if it exists
-include .env

# Default port values (can be overridden in .env)
DB_EXPOSED_PORT ?= 5432
REDIS_EXPOSED_PORT ?= 6379
BACKEND_EXPOSED_PORT ?= 8000
HTTP_EXPOSED_PORT ?= 8080
HTTPS_EXPOSED_PORT ?= 8443

DEV_DB_EXPOSED_PORT ?= 5433
DEV_REDIS_EXPOSED_PORT ?= 6380

# Default target
all: up

# Build and start the stack in detached mode
up:
	@echo "Starting the stack (Production)..."
	DB_EXPOSED_PORT=$(DB_EXPOSED_PORT) \
	REDIS_EXPOSED_PORT=$(REDIS_EXPOSED_PORT) \
	BACKEND_EXPOSED_PORT=$(BACKEND_EXPOSED_PORT) \
	HTTP_EXPOSED_PORT=$(HTTP_EXPOSED_PORT) \
	HTTPS_EXPOSED_PORT=$(HTTPS_EXPOSED_PORT) \
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(PROD_PROJECT) up -d --build

# Stop the stack
down:
	@echo "Stopping the stack (Production)..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(PROD_PROJECT) down

# Restart the stack
restart: down up

check_clean:
	@echo -n "Are you sure? This will delete all the data in this directory containers [y/N] " && read ans && [ $${ans:-N} = y ]

# Stop the stack and remove all volumes (WARNING: deletes DB data)
clean: check_clean
	@echo "Cleaning the stack (Production)..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(PROD_PROJECT) down -v

# Show logs
logs:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(PROD_PROJECT) logs -f

# Create Django Superuser (for admin panel)
createsuperuser:
	@echo "Creating Django superuser (Production)..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(PROD_PROJECT) exec api python manage.py createsuperuser

# Run migrations in production stack
makemigrations:
	@echo "Preparing migrations (Production)..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(PROD_PROJECT) exec api python manage.py makemigrations

migrate:
	@echo "Running migrations (Production)..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(PROD_PROJECT) exec api python manage.py migrate

# Create and setup virtual environment
dev-venv:
	@if [ ! -d ".venv" ]; then \
		echo "Creating virtual environment..."; \
		python3 -m venv .venv; \
	fi
	@echo "Installing/Updating requirements..."
	@. .venv/bin/activate && pip install --upgrade pip && pip install -r server/requirements.txt

VENV_PYTHON = ../.venv/bin/python3

# Start only DB and Redis for local dev
dev-up: dev-venv
	@echo "Starting DB and Redis (Dev)..."
	DB_EXPOSED_PORT=$(DEV_DB_EXPOSED_PORT) REDIS_EXPOSED_PORT=$(DEV_REDIS_EXPOSED_PORT) $(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(DEV_PROJECT) up -d db redis

dev-shell: dev-up
	@echo "Opening Django shell locally..."
	cd server && DB_HOST=127.0.0.1 DB_PORT=$(DEV_DB_EXPOSED_PORT) REDIS_HOST=127.0.0.1 REDIS_PORT=$(DEV_REDIS_EXPOSED_PORT) $(VENV_PYTHON) manage.py shell

dev-makemigrations: dev-up
	@echo "Running migrations locally (Dev)..."
	cd server && DB_HOST=127.0.0.1 DB_PORT=$(DEV_DB_EXPOSED_PORT) REDIS_HOST=127.0.0.1 REDIS_PORT=$(DEV_REDIS_EXPOSED_PORT) $(VENV_PYTHON) manage.py makemigrations

# Run migrations locally
dev-migrate: dev-up
	@echo "Running migrations locally (Dev)..."
	cd server && DB_HOST=127.0.0.1 DB_PORT=$(DEV_DB_EXPOSED_PORT) REDIS_HOST=127.0.0.1 REDIS_PORT=$(DEV_REDIS_EXPOSED_PORT) $(VENV_PYTHON) manage.py migrate

# Stop only DB and Redis
dev-down:
	@echo "Stopping DB and Redis (Dev)..."
	DB_EXPOSED_PORT=$(DEV_DB_EXPOSED_PORT) REDIS_EXPOSED_PORT=$(DEV_REDIS_EXPOSED_PORT) $(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(DEV_PROJECT) stop db redis

# Stop and wipe dev volumes (Isolated from production)
dev-clean: check_clean
	@echo "Cleaning dev stack..."
	DB_EXPOSED_PORT=$(DEV_DB_EXPOSED_PORT) REDIS_EXPOSED_PORT=$(DEV_REDIS_EXPOSED_PORT) $(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(DEV_PROJECT) down -v

# Show logs for dev stack
dev-logs:
	DB_EXPOSED_PORT=$(DEV_DB_EXPOSED_PORT) REDIS_EXPOSED_PORT=$(DEV_REDIS_EXPOSED_PORT) $(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(DEV_PROJECT) logs -f

# Run Django locally
dev-runserver: dev-up
	@echo "Running Django locally..."
	cd server && DB_HOST=127.0.0.1 DB_PORT=$(DEV_DB_EXPOSED_PORT) REDIS_HOST=127.0.0.1 REDIS_PORT=$(DEV_REDIS_EXPOSED_PORT) $(VENV_PYTHON) manage.py runserver

# Run tests locally (use TEST="module" to run specific tests)
dev-test: dev-up
	@echo "Running tests locally..."
	cd server && DB_HOST=127.0.0.1 DB_PORT=$(DEV_DB_EXPOSED_PORT) REDIS_HOST=127.0.0.1 REDIS_PORT=$(DEV_REDIS_EXPOSED_PORT) $(VENV_PYTHON) manage.py test $(TEST)

# Create superuser locally
dev-createsuperuser: dev-up
	@echo "Creating superuser locally..."
	cd server && DB_HOST=127.0.0.1 DB_PORT=$(DEV_DB_EXPOSED_PORT) REDIS_HOST=127.0.0.1 REDIS_PORT=$(DEV_REDIS_EXPOSED_PORT) $(VENV_PYTHON) manage.py createsuperuser

# Check container status
ps:
	@echo "--- Production Stack ---"
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(PROD_PROJECT) ps
	@echo "\n--- Dev Stack ---"
	DB_EXPOSED_PORT=$(DEV_DB_EXPOSED_PORT) REDIS_EXPOSED_PORT=$(DEV_REDIS_EXPOSED_PORT) $(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(DEV_PROJECT) ps

check_fclean:
	@echo -n "Are you sure? This will remove all the docker objects on the system (including other directories) [y/N] " && read ans && [ $${ans:-N} = y ]

# WARNING: Will prune all the docker objects on the system
fclean: check_fclean clean dev-clean
	@echo "Deep cleaning docker system..."
	docker system prune -a --volumes -f

re: clean up

.PHONY: all up down restart re clean check_clean check_fclean logs dev-logs ps fclean migrate dev-up dev-migrate dev-down dev-clean dev-runserver dev-test dev-createsuperuser dev-shell dev-venv
