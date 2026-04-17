# Shell configuration for git bash compatibility
ifeq ($(OS),Windows_NT)
	SHELL := C:/Program Files/Git/bin/bash.exe 
	ifeq ($(wildcard $(SHELL)),)
		SHELL := C:/Program Files/Git/usr/bin/bash.exe
	endif
	ifeq ($(wildcard $(SHELL)),)
		SHELL := C:/Program Files (x86)/Git/bin/bash.exe
	endif
	ifeq ($(wildcard $(SHELL)),)
		SHELL := C:/Program Files (x86)/Git/usr/bin/bash.exe
	endif
	export PATH := C:/Program Files/Git/usr/bin:$(PATH)
else
	SHELL := /bin/bash
endif
.SHELLFLAGS := -euo pipefail -c

.PHONY: help check-deps init-env init-bun db-reset db-migrate up down restart build rebuild logs clean network-create test unit-test int-test check-format-backend check-format-frontend check-format format-backend format-frontend format

# Colors for output
GREEN := \033[0;32m
RED := \033[0;31m
YELLOW := \033[0;33m
BLUE := \033[0;34m
CYAN := \033[0;36m
NC := \033[0m # No Color
CHECKMARK := [OK]
CROSSMARK := [NO]

# Project settings
PROJECT_NAME := stridetrack
NETWORK_NAME := $(PROJECT_NAME)-network

help: ## Show this help message
	@printf "$(CYAN)====================================================\n$(NC)"
	@printf "$(CYAN)  StrideTrack - Development Commands\n$(NC)"
	@printf "$(CYAN)====================================================\n\n$(NC)"
	@awk 'BEGIN {FS = ":.*##"; section=""} \
		/^[a-zA-Z_-]+:.*?##/ { \
			printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 \
		}' $(MAKEFILE_LIST)
	@printf "\n"

check-deps: ## Check if all required dependencies are installed
	@printf "$(BLUE)Checking dependencies...\n$(NC)\n"
	@command -v python >/dev/null 2>&1 && \
		[ "$$(python --version)" = "Python 3.13.9" ] && \
		printf "  $(GREEN)$(CHECKMARK)$(NC) Python:      $$(python --version)\n" || \
		printf "  $(RED)$(CROSSMARK)$(NC) Python:      Not 3.13.9 (found: $$(python --version 2>/dev/null || echo 'not installed'))\n"
	@command -v uv >/dev/null 2>&1 && \
		printf "  $(GREEN)$(CHECKMARK)$(NC) uv:          $$(uv --version)\n" || \
		printf "  $(RED)$(CROSSMARK)$(NC) uv:          Not found (install: curl -LsSf https://astral.sh/uv/install.sh | sh)\n"
	@command -v bun >/dev/null 2>&1 && \
		printf "  $(GREEN)$(CHECKMARK)$(NC) Bun:         $$(bun --version)\n" || \
		printf "  $(RED)$(CROSSMARK)$(NC) Bun:         Not found (install: curl -fsSL https://bun.sh/install | bash)\n"
	@bun x supabase --version >/dev/null 2>&1 && \
		printf "  $(GREEN)$(CHECKMARK)$(NC) bun x supabase:    $$(bun x supabase --version)\n" || \
		printf "  $(RED)$(CROSSMARK)$(NC) bun x supabase:    Not found (run: bun install)\n"
	@command -v docker >/dev/null 2>&1 && \
		printf "  $(GREEN)$(CHECKMARK)$(NC) Docker:      $$(docker --version 2>/dev/null)\n" || \
		printf "  $(RED)$(CROSSMARK)$(NC) Docker:      Not found\n"
	@printf "\n"

init-env: ## Copy .env.example files to .env in backend and frontend
	@printf "$(BLUE)Setting up environment files...\n\n$(NC)"
	@if [ -f backend/.env.example ]; then \
		if [ ! -f backend/.env ]; then \
			cp backend/.env.example backend/.env && \
			printf "  $(GREEN)$(CHECKMARK)$(NC) Created backend/.env\n"; \
		else \
			printf "  $(YELLOW)[WARNING]$(NC)  backend/.env already exists\n"; \
		fi \
	else \
		printf "  $(RED)$(CROSSMARK)$(NC) backend/.env.example not found\n"; \
	fi
	@if [ -f frontend/.env.example ]; then \
		if [ ! -f frontend/.env ]; then \
			cp frontend/.env.example frontend/.env && \
			printf "  $(GREEN)$(CHECKMARK)$(NC) Created frontend/.env\n"; \
		else \
			printf "  $(YELLOW)[WARNING]$(NC)  frontend/.env already exists\n"; \
		fi \
	else \
		printf "  $(YELLOW)[WARNING]$(NC)  frontend/.env.example not found (skipping)\n"; \
	fi
	@printf "\n"

db-migrate: ## Create a new database migration (usage: make db-migrate NAME="description")
	@if [ -z "$(NAME)" ]; then \
		printf "$(RED)Error: NAME is required\n$(NC)"; \
		printf "Usage: make db-migrate NAME=\"your_migration_name\"\n"; \
		exit 1; \
	fi
	@printf "$(BLUE)Creating migration: $(NAME)\n$(NC)"
	@bun x supabase migration new $(NAME)
	@printf "  $(GREEN)$(CHECKMARK)$(NC) Migration created\n"
	@printf "\n"

db-reset: ## Reset database with all migrations and seed data
	@printf "$(BLUE)Resetting database...\n$(NC)"
	@bun x supabase db reset
	@printf "  $(GREEN)$(CHECKMARK)$(NC) Database reset complete\n"
	@printf "\n"

init: check-deps init-env ## Initialize the entire project
	@printf "$(GREEN)$(CHECKMARK) Project initialization complete!\n$(NC)"
	@printf "\n"

network-create: ## Create Docker network for services
	@MSYS_NO_PATHCONV=1 docker network inspect $(NETWORK_NAME) >/dev/null 2>&1 || \
		(MSYS_NO_PATHCONV=1 docker network create $(NETWORK_NAME) && \
		printf "  $(GREEN)$(CHECKMARK)$(NC) Network $(NETWORK_NAME) created\n")

up: network-create ## Start all services (bun x supabase + App + Jaeger)
	@printf "$(BLUE)Starting bun x supabase...\n$(NC)"
	@bun x supabase start --exclude vector,analytics,realtime,storage
	@printf "\n"
	@printf "$(BLUE)Starting application services...\n$(NC)"
	@docker compose up -d
	@printf "\n"
	@printf "$(GREEN)$(CHECKMARK) All services started!\n$(NC)"
	@printf "  $(CYAN)bun x supabase Studio:$(NC) http://localhost:54323\n"
	@printf "  $(CYAN)API:$(NC) http://localhost:8000\n"
	@printf "  $(CYAN)Frontend:$(NC) http://localhost:5173\n"
	@printf "  $(CYAN)Jaeger UI:$(NC) http://localhost:16686\n"
	@printf "\n"

down: ## Stop all services
	@printf "$(BLUE)Stopping services...\n$(NC)"
	@docker compose down
	@bun x supabase stop
	@printf "  $(GREEN)$(CHECKMARK)$(NC) All services stopped\n"
	@printf "\n"

restart: ## Restart application services
	@printf "$(BLUE)Stopping application services...\n$(NC)"
	@docker compose down
	@printf "$(BLUE)Starting application services...\n$(NC)"
	@docker compose up -d
	@printf "  $(GREEN)$(CHECKMARK)$(NC) Application services restarted\n"
	@printf "\n"

build: ## Build application containers
	@printf "$(BLUE)Building containers...\n$(NC)"
	@docker compose build
	@printf "  $(GREEN)$(CHECKMARK)$(NC) Build complete\n"
	@printf "\n"

rebuild: ## Rebuild application services
	@printf "$(BLUE)Stopping application services...\n$(NC)"
	@docker compose down
	@printf "$(BLUE)Building containers...\n$(NC)"
	@docker compose build --no-cache
	@printf "$(BLUE)Starting application services...\n$(NC)"
	@docker compose up -d
	@printf "  $(GREEN)$(CHECKMARK)$(NC) Application Services Rebuilt\n"
	@printf "\n"

logs: ## View logs (usage: make logs SERVICE=backend)
	@if [ -z "$(SERVICE)" ]; then \
		docker compose logs -f; \
	else \
		docker compose logs -f $(SERVICE); \
	fi

clean: ## Remove all containers, networks, and volumes
	@printf "$(YELLOW)Cleaning up...\n$(NC)"
	@docker compose down -v
	@bun x supabase stop --no-backup
	@docker network rm $(NETWORK_NAME) 2>/dev/null || true
	@printf "  $(GREEN)$(CHECKMARK)$(NC) Cleanup complete\n"
	@printf "\n"

unit-test: ## Run unit tests locally (no Supabase required)
	@printf "$(BLUE)Running unit tests...\n$(NC)"
	@cd backend && uv run pytest tests/unit/ -v --tb=short
	@printf "  $(GREEN)$(CHECKMARK)$(NC) Unit tests complete\n"
	@printf "\n"

int-test: ## Run integration tests in container against local Supabase (requires: make up)
	@if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -q 'supabase_kong_StrideTrack'; then \
		printf "$(RED)$(CROSSMARK) Supabase is not running.\n$(NC)"; \
		printf "  Run $(CYAN)make up$(NC) first, then retry $(CYAN)make int-test$(NC)\n\n"; \
		exit 1; \
	fi
	@printf "$(BLUE)Building test container...\n$(NC)"
	@docker build -f backend/Dockerfile.test -t $(PROJECT_NAME)-test backend/
	@printf "$(BLUE)Running integration tests...\n$(NC)"
	$(eval SERVICE_KEY := $(shell bun x supabase status -o json 2>/dev/null | grep -o '"SERVICE_ROLE_KEY": "[^"]*"' | cut -d'"' -f4))
	@docker run --rm \
		--network supabase_network_StrideTrack \
		-e SUPABASE_URL=http://supabase_kong_StrideTrack:8000 \
		-e SUPABASE_SERVICE_ROLE_KEY="$(SERVICE_KEY)" \
		-e ENVIRONMENT=test \
		-e OTEL_SDK_DISABLED=true \
		$(PROJECT_NAME)-test uv run pytest tests/integration/ -v --tb=short
	@printf "  $(GREEN)$(CHECKMARK)$(NC) Integration tests complete\n"
	@printf "\n"

test: ## Run all tests (unit + integration against local Supabase)
	@$(MAKE) unit-test
	@$(MAKE) int-test

check-format-backend: ## Check code linting and formatting in the backend with Ruff
	@printf "$(BLUE)Checking Backend Linting...\n$(NC)"
	@cd backend && uv run ruff check .
	@printf "  $(GREEN)$(CHECKMARK)$(NC) Backend linting passed\n"
	@printf "$(BLUE)Checking Backend Formatting...\n$(NC)"
	@cd backend && uv run ruff format --check .
	@printf "  $(GREEN)$(CHECKMARK)$(NC) Backend formatting passed\n"
	@printf "\n"

check-format-frontend: ## Check code linting and formatting in the frontend with Eslint and Prettier
	@printf "$(BLUE)Checking Frontend Linting...\n$(NC)"
	@cd frontend && bun run lint
	@printf "  $(GREEN)$(CHECKMARK)$(NC) Frontend linting passed\n"
	@printf "$(BLUE)Checking Frontend Formatting...\n$(NC)"
	@cd frontend && bun run check-format
	@printf "  $(GREEN)$(CHECKMARK)$(NC) Frontend formatting passed\n"
	@printf "\n"

check-format: ## Check code linting and formatting in both backend and frontend
	@$(MAKE) check-format-backend
	@$(MAKE) check-format-frontend

format-backend: ## Format backend code with Ruff
	@printf "$(BLUE)Fixing Backend Linting...\n$(NC)"
	@cd backend && uv run ruff check --fix .
	@printf "  $(GREEN)$(CHECKMARK)$(NC) Backend linting fixed\n"
	@printf "$(BLUE)Formatting Backend Code...\n$(NC)"
	@cd backend && uv run ruff format .
	@printf "  $(GREEN)$(CHECKMARK)$(NC) Backend formatting complete\n"
	@printf "\n"

format-frontend: ## Format frontend code with Prettier
	@printf "$(BLUE)Formatting Frontend Code...\n$(NC)"
	@cd frontend && bun run format
	@printf "  $(GREEN)$(CHECKMARK)$(NC) Frontend formatting complete\n"
	@printf "\n"

format: ## Format code in both backend and frontend
	@$(MAKE) format-backend
	@$(MAKE) format-frontend