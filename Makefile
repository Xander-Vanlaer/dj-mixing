.PHONY: help build up down restart logs clean test

help: ## Show this help message
	@echo "DJ Mixing Platform - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d
	@echo "Services started. Access the app at:"
	@echo "  Frontend:  http://localhost:3000"
	@echo "  Backend:   http://localhost:8000"
	@echo "  API Docs:  http://localhost:8000/docs"

down: ## Stop all services
	docker-compose down

restart: ## Restart all services
	docker-compose restart

logs: ## Show logs from all services
	docker-compose logs -f

logs-backend: ## Show backend logs
	docker-compose logs -f backend

logs-frontend: ## Show frontend logs
	docker-compose logs -f frontend

status: ## Show service status
	docker-compose ps

shell-backend: ## Open shell in backend container
	docker-compose exec backend /bin/bash

shell-db: ## Open PostgreSQL shell
	docker-compose exec db psql -U djuser -d djmixing

clean: ## Remove all containers and volumes (WARNING: deletes data)
	docker-compose down -v
	@echo "All containers and volumes removed"

backup-db: ## Backup database
	docker-compose exec db pg_dump -U djuser djmixing > backup-$$(date +%Y%m%d-%H%M%S).sql
	@echo "Database backed up"

restore-db: ## Restore database from backup.sql
	docker-compose exec -T db psql -U djuser djmixing < backup.sql
	@echo "Database restored"

install: ## Initial setup - create .env and build
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file. Please edit it with your configuration."; \
	fi
	make build
	@echo "Installation complete. Run 'make up' to start."

dev-backend: ## Run backend in development mode
	cd backend && uvicorn app.main:app --reload

dev-frontend: ## Run frontend in development mode
	cd frontend && npm start

test-backend: ## Run backend tests
	cd backend && pytest

update: ## Update and rebuild
	git pull
	make build
	make restart
