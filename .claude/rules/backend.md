## Backend Rules

- Always use type annotations on all function parameters and return types (Ruff ANN rules enforced)
- Use Pydantic models for all request/response schemas
- Never put business logic in route handlers — delegate to services
- Never put HTTP concerns in repositories — they only interact with Supabase
- Use `backend/app/core/config.py` (Settings class) for all environment variables
- Ruff config is in `backend/pyproject.toml` — do not override inline
- Use `uv` as the package manager (not pip directly)
- Python version is pinned to 3.13.9 (see `backend/.python-version`)
