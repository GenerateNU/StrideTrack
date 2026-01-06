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

.PHONY: help check-deps init-env init-bun db-reset db-migrate up down restart build rebuild logs clean network-create

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

up: network-create ## Start all services (bun x supabase + App + SigNoz)
	@printf "$(BLUE)Starting bun x supabase...\n$(NC)"
	@bun x supabase start --exclude vector
	@printf "\n"
	@printf "$(BLUE)Starting application services...\n$(NC)"
	@docker compose up -d
	@printf "\n"
	@printf "$(GREEN)$(CHECKMARK) All services started!\n$(NC)"
	@printf "  $(CYAN)bun x supabase Studio:$(NC) http://localhost:54323\n"
	@printf "  $(CYAN)API:$(NC) http://localhost:8000\n"
	@printf "  $(CYAN)Frontend:$(NC) http://localhost:5173\n"
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
