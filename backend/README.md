# StrideTrack Backend

FastAPI application providing REST API for StrideTrack biomechanical data collection and analysis.

## Architecture

This backend follows a **layered architecture** pattern with clear separation of concerns:

```
Routes → Services → Repositories → Database (Supabase)
```

**Design Principles:**

- **Routes:** Thin layer handling HTTP concerns (request/response, status codes)
- **Services:** Business logic and validation
- **Repositories:** Database operations via Supabase SDK
- **Exceptions:** Custom exceptions raised in repo/service, converted to HTTP responses via handlers

## Directory Structure

```
backend/
├── app/
│   ├── api.py                    # API router aggregation
│   ├── main.py                   # FastAPI app initialization
│   ├── core/                     # Core configuration
│   │   ├── config.py            # Settings via pydantic-settings
│   │   ├── observability.py     # OpenTelemetry setup
│   │   └── supabase.py          # Supabase client initialization
│   ├── routes/                   # API endpoints
│   │   └── example_routes.py    # Example CRUD endpoints
│   ├── services/                 # Business logic
│   │   └── example_service.py   # Example service layer
│   ├── repositories/             # Database operations
│   │   └── example_repository.py # Example repository layer
│   ├── schemas/                  # Pydantic models
│   │   └── example_schemas.py   # Request/response schemas
│   └── exceptions.py             # Custom exceptions
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Environment template
├── .dockerignore                 # Docker build exclusions
├── Dockerfile.dev                # Development container
├── Dockerfile.prod               # Production container
├── pyproject.toml                # Project dependencies (uv)
└── uv.lock                       # Locked dependencies
```

## Data Flow

**Request Flow:**

1. HTTP Request → **Route** (validates with Pydantic schema)
2. Route → **Service** (business logic, validation)
3. Service → **Repository** (database operations)
4. Repository → **Supabase SDK** → Database

**Error Flow:**

- Repository raises `NotFoundException` if record not found
- Service raises `ValueError` for validation errors
- Exception handlers convert to proper HTTP responses (404, 400, etc)
- All errors logged with trace context via OpenTelemetry

## Observability

**OpenTelemetry Integration:**

- Automatic request tracing via `FastAPIInstrumentor`
- HTTPX instrumentation for Supabase calls
- Logs automatically correlated with traces (trace_id, span_id)
- OTLP export to local Jaeger (gRPC `localhost:4317`, HTTP `localhost:4318`)
- Jaeger UI available at `http://localhost:16686` when running the dev stack

**Logging:**

```python
import logging
logger = logging.getLogger(__name__)

# Logs automatically include trace_id and span_id
logger.info("Processing request")
logger.error("Something failed", exc_info=True)
```

## Database

**Supabase SDK:**

- Async client via `get_async_supabase()` dependency
- All operations through REST API (not direct Postgres)
- Row Level Security policies defined in migrations

**Migrations:**

- Managed via Supabase CLI
- Located in `../supabase/migrations/`
- Apply with `make db-reset` (local) or `supabase db push` (production)

## Development

**Run locally:**

```bash
# From project root
make up            # Start all services
make db-reset      # Apply migrations
make logs SERVICE=backend  # View logs
```

**Add new feature:**

1. Create migration: `make db-migrate NAME="add_feature"`
2. Create schema in `app/schemas/`
3. Create repository in `app/repositories/`
4. Create service in `app/services/`
5. Create routes in `app/routes/`
6. Register router in `app/api.py`

**Testing endpoints:**

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

See `.env.example` for required configuration:

- `ENVIRONMENT` - "development" or "production"
- `SUPABASE_URL` - Supabase API URL
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase admin key
- `OTEL_ENDPOINT` - OpenTelemetry collector endpoint
- `OTEL_PYTHON_LOG_CORRELATION` - Enable trace/log correlation

## Design Patterns

**Dependency Injection:**
FastAPI's dependency system injects Supabase client and service instances into routes.

**Repository Pattern:**
Encapsulates all database logic, making it easy to swap Supabase for another backend.

**Exception Handling:**
Domain exceptions (NotFoundException, ValueError) are caught by global handlers and converted to appropriate HTTP responses.

**Logging Strategy:**
Structured logging with automatic trace context injection via OpenTelemetry for distributed tracing.
