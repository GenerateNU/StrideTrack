## Testing Rules

- Every new backend service function must have a corresponding unit test
- Bug fixes must include a regression test that reproduces the bug
- Unit tests go in `backend/tests/unit/` — these run without Supabase
- Integration tests go in `backend/tests/integration/` — these require `make up` first
- Test file naming: `test_{feature}.py`
- Run unit tests: `make unit-test`
- Run integration tests: `make int-test`
- Run all tests: `make test`
- Tests should verify behavior, not implementation details
- Mock only external boundaries (Supabase client, external APIs), not internal functions
