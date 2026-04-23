# https://www.gnu.org/software/make/manual/make.html

NAME = transcendence

DOCKER_COMPOSE = docker compose
DOCKER_COMPOSE_FILE = ./devops/docker-compose.yml
PROD_PROJECT = prod-transcendence
DEV_PROJECT = dev-transcendence

# Default target
all: up

# Build and start the stack in detached mode
up:
	@echo "Starting the stack (Production)..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(PROD_PROJECT) up -d --build

# Stop the stack
down:
	@echo "Stopping the stack (Production)..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(PROD_PROJECT) down

# Restart the stack
restart: down up

check_clean:
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]

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
migrate:
	@echo "Running migrations (Production)..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(PROD_PROJECT) exec api python manage.py migrate

# Start only DB and Redis for local dev
dev-deps:
	@echo "Starting DB and Redis (Dev)..."
	DB_PORT=5433 REDIS_PORT=6380 $(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(DEV_PROJECT) up -d db redis

# Run migrations locally
dev-migrate: dev-deps
	@echo "Running migrations locally (Dev)..."
	cd server && DB_HOST=127.0.0.1 DB_PORT=5433 REDIS_HOST=127.0.0.1 REDIS_PORT=6380 python3 manage.py migrate

# Stop only DB and Redis
dev-down:
	@echo "Stopping DB and Redis (Dev)..."
	DB_PORT=5433 REDIS_PORT=6380 $(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(DEV_PROJECT) stop db redis

# Stop and wipe dev volumes (Isolated from production)
dev-clean: check_clean
	@echo "Cleaning dev stack..."
	DB_PORT=5433 REDIS_PORT=6380 $(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(DEV_PROJECT) down -v

# Run Django locally
dev-runserver: dev-deps
	@echo "Running Django locally..."
	cd server && DB_HOST=127.0.0.1 DB_PORT=5433 REDIS_HOST=127.0.0.1 REDIS_PORT=6380 python3 manage.py runserver

# Run tests locally
dev-test: dev-deps
	@echo "Running tests locally..."
	cd server && DB_HOST=127.0.0.1 DB_PORT=5433 REDIS_HOST=127.0.0.1 REDIS_PORT=6380 python3 manage.py test

# Create superuser locally
dev-createsuperuser: dev-deps
	@echo "Creating superuser locally..."
	cd server && DB_HOST=127.0.0.1 DB_PORT=5433 REDIS_HOST=127.0.0.1 REDIS_PORT=6380 python3 manage.py createsuperuser

# Check container status
ps:
	@echo "--- Production Stack ---"
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(PROD_PROJECT) ps
	@echo "\n--- Dev Stack ---"
	DB_PORT=5433 REDIS_PORT=6380 $(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) -p $(DEV_PROJECT) ps

# Prune unused docker objects
fclean: clean
	@echo "Deep cleaning docker system..."
	docker system prune -a --volumes -f

re: fclean up

.PHONY: all up down restart re clean check_clean logs ps fclean migrate dev-deps dev-migrate dev-down dev-clean dev-runserver dev-test dev-createsuperuser
