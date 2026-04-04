# StrideTrack

## Tech Stack

- **Frontend:** Bun + React 19 / Vite + TypeScript + TailwindCSS
- **Backend:** Python 3.13 + FastAPI + Pydantic
- **Database:** Supabase (Postgres + Auth)
- **Containerized:** Docker Compose
- **Backend tooling:** uv (package manager), Ruff (linter/formatter)
- **Frontend tooling:** ESLint (linter), Prettier (formatter)
- **Observability:** OpenTelemetry + Jaeger

## Architecture

Backend follows **route → service → repository** pattern:

- `backend/app/routes/` — Request validation only, delegates to services
- `backend/app/services/` — Business logic, error handling
- `backend/app/repositories/` — Database operations only (Supabase client)
- `backend/app/core/` — Settings, auth, config, exceptions
- `backend/tests/unit/` — Unit tests (no Supabase required)
- `backend/tests/integration/` — Integration tests (requires running Supabase)

Frontend:

- `frontend/src/pages/` — Page components (React Router)
- `frontend/src/components/` — Reusable UI components
- `frontend/src/hooks/` — Custom hooks (`*.hooks.ts`)
- `frontend/src/context/` — React Context providers
- `frontend/src/lib/` — Utilities, API client, config

## Development Commands

All commands via Makefile in project root:

- `make check-format` — Check linting + formatting (backend + frontend)
- `make format` — Auto-fix formatting issues
- `make unit-test` — Run backend unit tests (no Supabase needed)
- `make int-test` — Integration tests (requires `make up` first)
- `make build` — Build Docker containers
- `make up` / `make down` — Start/stop all services
- `make init` — Initialize project (check deps + setup env files)

## Coding Standards

### Python

- Pydantic models for all request/response schemas
- Ruff for linting and formatting (config in `backend/pyproject.toml`)
- Type annotations on all function parameters and return types
- Central `backend/app/core/config.py` for all environment variables

### TypeScript

- Zod schemas for runtime validation
- TanStack Query for all server state (no manual fetch/useEffect)
- React Router for navigation
- File naming: `*.hooks.ts`, `*.service.ts`
- TailwindCSS for styling

### General

- Strong typing everywhere (params, returns, variables)
- Descriptive, extension-based file naming
- No secrets or `.env` files in commits

## Git Workflow

- **NOT auto-approved:** `git push`, production deploys, DB migrations
- Always verify `make check-format` and `make unit-test` pass before committing
