.PHONY: help install dev-install test lint format run run-dev build deploy

help:
	@echo "Available commands:"
	@echo "install     - Install production dependencies"
	@echo "dev-install - Install development dependencies"
	@echo "test        - Run tests"
	@echo "lint        - Run linting"
	@echo "format      - Format code"
	@echo "run         - Run production server"
	@echo "run-dev     - Run development server"
	@echo "build       - Build Docker images"
	@echo "deploy      - Deploy to production"

install:
	poetry install --no-dev

dev-install:
	poetry install

test:
	./scripts/run-tests.sh

lint:
	./scripts/lint.sh

format:
	poetry run black app tests

run:
	docker-compose up --build

run-dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build

build:
	docker-compose build

deploy:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
