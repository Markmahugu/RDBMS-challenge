.PHONY: help install install-frontend install-backend dev dev-frontend dev-backend build build-frontend build-backend clean clean-frontend clean-backend lint lint-frontend lint-backend format format-frontend format-backend test test-frontend test-backend docker-build docker-up docker-down setup

# Default target
help: ## Show this help message
	@echo "WebRDBMS Monorepo - Development Commands"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

# Installation
install: ## Install all dependencies (root, frontend, backend)
	npm install
	cd frontend && npm install
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

# Development
dev: ## Run both frontend and backend in development mode
	concurrently "make dev-backend" "make dev-frontend"

dev-frontend: ## Run frontend in development mode
	cd frontend && npm run dev

dev-backend: ## Run backend in development mode
	cd backend && python -m app.main

# Building
build: build-frontend ## Build all components

build-frontend: ## Build frontend for production
	cd frontend && npm run build

build-backend: ## Build backend (no-op for now)
	@echo "Backend uses interpreted Python, no build step needed"

# Cleaning
clean: clean-frontend clean-backend ## Clean all build artifacts
	npm run clean

clean-frontend: ## Clean frontend build artifacts
	cd frontend && rm -rf node_modules dist .next

clean-backend: ## Clean backend build artifacts
	cd backend && rm -rf __pycache__ *.pyc *.pyo .pytest_cache .coverage htmlcov

# Code Quality
lint: lint-frontend lint-backend ## Lint all code

lint-frontend: ## Lint frontend code
	cd frontend && npm run lint

lint-backend: ## Lint backend code
	cd backend && black --check app/ && isort --check-only app/ && mypy app/

format: format-frontend format-backend ## Format all code

format-frontend: ## Format frontend code
	cd frontend && npm run format

format-backend: ## Format backend code
	cd backend && black app/ && isort app/

# Testing
test: test-frontend test-backend ## Run all tests

test-frontend: ## Run frontend tests
	cd frontend && npm test

test-backend: ## Run backend tests
	cd backend && python -m pytest

# Docker
docker-build: ## Build Docker containers
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up

docker-down: ## Stop Docker containers
	docker-compose down

# Setup
setup: ## Initial project setup
	@echo "Setting up WebRDBMS monorepo..."
	make install
	@echo "Setup complete! Run 'make dev' to start development servers."

# Development helpers
update-deps: ## Update all dependencies
	cd frontend && npm update
	cd backend && pip install --upgrade -r requirements.txt

check-health: ## Check health of both services
	@echo "Checking backend health..."
	@curl -s http://localhost:8000/ > /dev/null && echo "✅ Backend is running" || echo "❌ Backend is not running"
	@echo "Checking frontend health..."
	@curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend is running" || echo "❌ Frontend is not running"

logs: ## Show logs from running containers
	docker-compose logs -f

# Database operations
db-reset: ## Reset database to demo data
	curl -X POST http://localhost:8000/databases/DemoDB/reset

db-query: ## Execute a test query (usage: make db-query query="SELECT * FROM employees")
	@curl -X POST http://localhost:8000/databases/DemoDB/query \
		-H "Content-Type: application/json" \
		-d '{"query": "$(query)"}' | jq .

# Git helpers
commit: ## Commit changes with conventional commit (usage: make commit msg="feat: add new feature")
	git add .
	git commit -m "$(msg)"

push: ## Push changes to remote
	git push origin main

# Environment
env-dev: ## Set up development environment
	cp .env.example .env 2>/dev/null || echo "No .env.example found"
	cd backend && cp .env.example .env 2>/dev/null || echo "No backend .env.example found"
	cd frontend && cp .env.example .env 2>/dev/null || echo "No frontend .env.example found"
