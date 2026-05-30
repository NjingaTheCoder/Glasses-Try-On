.PHONY: help up down build logs shell migrate makemigrations createsuperuser seed test clean

help:
	@echo "WearLens - Available Commands:"
	@echo "  make up              - Start all services"
	@echo "  make down            - Stop all services"
	@echo "  make build           - Rebuild all containers"
	@echo "  make logs            - View all logs"
	@echo "  make logs-api        - View API logs"
	@echo "  make logs-celery     - View Celery logs"
	@echo "  make logs-web        - View frontend logs"
	@echo "  make shell           - Open Django shell"
	@echo "  make migrate         - Run database migrations"
	@echo "  make makemigrations  - Create new migrations"
	@echo "  make createsuperuser - Create Django superuser"
	@echo "  make seed            - Seed sample data"
	@echo "  make test            - Run all tests"
	@echo "  make test-api        - Run backend tests"
	@echo "  make test-web        - Run frontend tests"
	@echo "  make lint            - Lint all code"
	@echo "  make format          - Format all code"
	@echo "  make clean           - Clean up containers and volumes"

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

logs:
	docker compose logs -f

logs-api:
	docker compose logs -f api

logs-celery:
	docker compose logs -f celery

logs-web:
	docker compose logs -f web

shell:
	docker compose exec api python manage.py shell

migrate:
	docker compose exec api python manage.py migrate

makemigrations:
	docker compose exec api python manage.py makemigrations

createsuperuser:
	docker compose exec api python manage.py createsuperuser

seed:
	docker compose exec api python /app/scripts/seed.py

test:
	@echo "Running backend tests..."
	docker compose exec api pytest
	@echo "Running frontend tests..."
	docker compose exec web npm test

test-api:
	docker compose exec api pytest -v

test-web:
	docker compose exec web npm test

lint:
	@echo "Linting backend..."
	docker compose exec api ruff check .
	@echo "Linting frontend..."
	docker compose exec web npm run lint

format:
	@echo "Formatting backend..."
	docker compose exec api black .
	docker compose exec api ruff check --fix .
	@echo "Formatting frontend..."
	docker compose exec web npm run format

clean:
	docker compose down -v
	docker system prune -f
