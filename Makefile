# https://www.gnu.org/software/make/manual/make.html

NAME = transcendence

DOCKER_COMPOSE = docker-compose
DOCKER_COMPOSE_FILE = ./devops/docker-compose.yml

# Default target
all: up

# Build and start the stack in detached mode
up:
	@echo "Starting the stack..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) up -d --build

# Stop the stack
down:
	@echo "Stopping the stack..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down

# Restart the stack
restart: down up

check_clean:
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]

# Stop the stack and remove all volumes (WARNING: deletes DB data)
clean: check_clean
	@echo "Cleaning the stack (removing volumes)..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) down -v

# Show logs
logs:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) logs -f

# Create Django Superuser (for admin panel)
createsuperuser:
	@echo "Creating Django superuser..."
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) exec api python manage.py createsuperuser

# Check container status
ps:
	$(DOCKER_COMPOSE) -f $(DOCKER_COMPOSE_FILE) ps

# Prune unused docker objects
fclean: clean
	@echo "Deep cleaning docker system..."
	docker system prune -a --volumes -f

re: fclean up

.PHONY: all up down restart re clean check_clean logs ps fclean
