# StrideTrack

**The Future of Track Training**

StrideTrack replaces manual video analysis for track and field coaches with real-time biomechanical feedback. Using shoe-mounted sensors, coaches get instant access to ground contact time, step counting, fly time, and hurdle splits.

## Purpose

This is a 13-week prototype development project with Generate (generatenu.com) to build a production-ready dual-sensor system and analytics dashboard for track and field coaches.

## Tech Stack

**Backend:**

- FastAPI (Python 3.13.9)
- Supabase (Database & Auth)
- OpenTelemetry (Observability)
- uv (Package Management)

**Frontend:**

- React 19 + Vite
- TanStack Query (Server State)
- Tailwind CSS + shadcn/ui
- Bun (Package Management)

**Infrastructure:**

- Docker & Docker Compose
- Supabase (Local Development)
- Make (Task Automation)

## Project Structure

```
stridetrack/
├── backend/              # FastAPI application (see backend/README.md)
├── frontend/             # React application (see frontend/README.md)
├── supabase/             # Database migrations and seed data
│   ├── migrations/       # SQL migrations
│   ├── seed.sql          # Seed data for local dev
│   └── config.toml       # Supabase configuration
├── docker-compose.yml    # Application services
├── otel-collector-config.yaml
├── Makefile              # Development commands
├── DEPENDENCIES.md       # Installation guide
└── README.md
```

## Dependencies

See [DEPENDENCIES.md](DEPENDENCIES.md) for detailed installation instructions.

**Required:** Docker, Bun, Python 3.13.9, uv, Make

**Verify installation:**

```bash
make check-deps
```

## Quickstart

1. **Clone and setup:**

   ```bash
   git clone <repo-url>
   cd stridetrack
   make init          # Check deps, create .env files
   ```

2. **Configure environment:**
   Edit `backend/.env` with your settings (defaults work for local dev)

3. **Start services:**

   ```bash
   make up            # Starts Supabase + Backend
   make db-reset      # Apply migrations and seed data
   ```

4. **Access services:**
   - API Documentation: http://localhost:8000/docs
   - Supabase Studio: http://localhost:54323
   - API: http://localhost:8000

## Development Commands

| Command                              | Description                                    |
| ------------------------------------ | ---------------------------------------------- |
| `make help`                          | Show all available commands                    |
| `make up`                            | Start all services                             |
| `make down`                          | Stop all services                              |
| `make build`                         | Build containers                               |
| `make rebuild`                       | Rebuild containers without cache               |
| `make restart`                       | Restart application services                   |
| `make logs`                          | View all logs (or `make logs SERVICE=backend`) |
| `make db-migrate NAME="description"` | Create new migration                           |
| `make db-reset`                      | Reset database with migrations                 |
| `make clean`                         | Remove all containers and volumes              |

## Documentation

- **Backend:** See [backend/README.md](backend/README.md) for API architecture and design patterns
- **Frontend:** See [frontend/README.md](frontend/README.md) for React architecture and hooks patterns

## Contributing

This project is developed as part of Generate NU's 13-week development program. Focus is on software components (dashboard, data pipeline, analytics) with mock data support.


## Environment Setup

### Supabase
Copy `supabase/.env.example` to `supabase/.env` and fill in:
- `GOOGLE_CLIENT_ID` - From Google Cloud Console OAuth credentials
- `GOOGLE_CLIENT_SECRET` - From Google Cloud Console OAuth credentials

To get these:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth 2.0 credentials
3. Add redirect URI: `http://127.0.0.1:54321/auth/v1/callback`