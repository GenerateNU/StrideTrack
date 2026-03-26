# Backend Testing Guide

## Overview

Tests are split into two types:

| Type | Location | Needs Supabase? | When to run |
|------|----------|-----------------|-------------|
| **Unit** | `tests/unit/` | No | Always — fast, pure functions |
| **Integration** | `tests/integration/` | Yes | Against a live Supabase instance |

---

## Running Tests

```bash
# Unit tests only (no services needed)
make unit-test

# Integration tests (requires: make up first)
make int-test

# All tests
make test
```

Or run directly with pytest:

```bash
cd backend

# Unit tests
uv run pytest tests/unit/ -v

# Integration tests
uv run pytest tests/integration/ -v

# Specific file
uv run pytest tests/unit/test_stride_metrics.py -v

# Specific test
uv run pytest -k test_calculate_total_steps -v

# With coverage
uv run pytest tests/ --cov=app/services --cov=app/utils --cov-report=term-missing
```

---

## Directory Structure

```
backend/tests/
├── conftest.py              # Shared fixtures: test_client, supabase_client, cleanup
├── factories/               # Test data builders — use factories, never hardcode data
│   ├── athlete_factory.py
│   ├── coach_factory.py
│   ├── csv_factory.py
│   └── example_factory.py
├── unit/                    # Pure function tests — no DB, no network
│   └── test_example_utils.py
└── integration/             # Route-level tests — hit real Supabase
    └── test_example.py
```

---

## Integration Tests: Cleanup Contract

Tests run against a **real Supabase instance** (production or a dedicated test environment). Every test that creates data **must clean up after itself** to avoid polluting the database. This is also what makes parallel CI runs safe.

### The `created_ids` fixture

Every integration test that creates DB records must use the `created_ids` fixture and register each created ID:

```python
def test_create_athlete(self, test_client: TestClient, created_ids: dict) -> None:
    response = test_client.post("/api/athletes", json=AthleteFactory.create())

    assert response.status_code == 201
    # Register the ID — cleanup happens automatically after this test
    created_ids["athlete_ids"].append(response.json()["athlete_id"])
```

The `cleanup_created` autouse fixture in `conftest.py` runs after every test and deletes only the IDs registered in `created_ids`. This means:

- **No test data persists** after the test completes
- **Parallel CI runs don't interfere** — each test only touches its own records
- **No global deletes** — we never delete all records from a table

### Cleanup order (FK-safe)

Records are deleted in this order to avoid FK constraint violations:
1. `run_metrics` (by `run_id`)
2. `run` (by `run_id`)
3. `athletes` (by `athlete_id`)
4. `coaches` (by `coach_id`)
5. `training_runs` (by `id`) — independent, no FK dependencies

### Tests that delete their own records

If a test explicitly deletes a record (e.g. `TestDeleteAthlete.test_delete_existing_athlete`), do **not** also register it in `created_ids` — that would cause a no-op delete on cleanup:

```python
def test_delete_existing_athlete(self, test_client, created_ids):
    create_response = test_client.post("/api/athletes", json=AthleteFactory.create())
    athlete_id = create_response.json()["athlete_id"]
    # Don't add to created_ids — this test deletes it itself

    response = test_client.delete(f"/api/athletes/{athlete_id}")
    assert response.status_code == 204
```

---

## FK Dependency Order

The database has the following FK chain:

```
coaches → athletes → run → run_metrics
```

Always create parents before children. Use `supabase_client` directly for records that have no API endpoint (like `coaches`):

```python
# Create coach via supabase_client (no API endpoint)
coach_resp = supabase_client.table("coaches").insert(CoachFactory.create()).execute()
coach_id = coach_resp.data[0]["coach_id"]
created_ids["coach_ids"].append(coach_id)

# Create athlete via API using that coach_id
athlete_data = AthleteFactory.create(coach_id=coach_id)
response = test_client.post("/api/athletes", json=athlete_data)
created_ids["athlete_ids"].append(response.json()["athlete_id"])
```

Cleanup happens in reverse FK order automatically (run_metrics → run → athletes → coaches).

---

## Writing a New Integration Test

1. Add `@pytest.mark.integration` to the class
2. Accept `test_client: TestClient` and `created_ids: dict` as parameters
3. Create records via the API (not directly via supabase_client)
4. Register every created ID in `created_ids` immediately after creation
5. Follow Arrange → Act → Assert

```python
@pytest.mark.integration
class TestMyFeature:
    def test_create_something(
        self, test_client: TestClient, created_ids: dict
    ) -> None:
        # Arrange
        athlete = AthleteFactory.create()
        athlete_resp = test_client.post("/api/athletes", json=athlete)
        assert athlete_resp.status_code == 201
        athlete_id = athlete_resp.json()["athlete_id"]
        created_ids["athlete_ids"].append(athlete_id)  # ← register for cleanup

        # Act
        response = test_client.post("/api/something", json={"athlete_id": athlete_id})

        # Assert
        assert response.status_code == 201
```

---

## Writing a New Unit Test

Unit tests are pure Python — no fixtures, no DB, no imports from `conftest.py`:

```python
@pytest.mark.unit
class TestMyFunction:
    def test_happy_path(self) -> None:
        df = pd.DataFrame({"gct_ms": [200, 210]})
        result = my_function(df)
        assert result == 205.0

    def test_empty_input(self) -> None:
        result = my_function(pd.DataFrame(columns=["gct_ms"]))
        assert result == 0.0
```

Use worked examples from docstrings as the basis for test cases.

---

## CI Workflow

Tests run on every PR to `main` that touches `backend/**`. There are two parallel jobs:

**`unit-tests`** — runs `pytest tests/unit/` with no secrets, no services. Fast.

**`integration-tests`** — runs `pytest tests/integration/` with `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` injected from GitHub repo secrets. These tests hit the live Supabase database and clean up after themselves.

To set up CI integration tests, add these secrets to your GitHub repository:
- `SUPABASE_URL` — your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY` — your Supabase service role key (bypasses RLS)

See `.github/workflows/backend-tests.yml` for the full workflow definition.

---

## Auth Routes

`GET /api/auth/me` and `GET /api/auth/me/coach` require a valid Supabase JWT token. These endpoints are not currently covered by integration tests since they require a real authenticated user session. They can be tested manually via the Swagger UI at `/docs`.
