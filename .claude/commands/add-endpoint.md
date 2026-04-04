Create a new backend API endpoint following the route → service → repository pattern.

Resource name: $ARGUMENTS

For the resource "$ARGUMENTS", create or update these files:

1. **Schema** — `backend/app/schemas/$ARGUMENTS.py`
   - Pydantic request/response models with full type annotations
   - Follow existing schema patterns in the schemas directory

2. **Repository** — `backend/app/repositories/${ARGUMENTS}_repository.py`
   - Supabase database operations only
   - No business logic, no HTTP concerns
   - Follow existing repository patterns

3. **Service** — `backend/app/services/${ARGUMENTS}_service.py`
   - Business logic and error handling
   - Call repository methods for DB access
   - Raise appropriate exceptions from `backend/app/core/exceptions.py`

4. **Routes** — `backend/app/routes/${ARGUMENTS}_routes.py`
   - FastAPI route handlers
   - Input validation only, delegate to service
   - Proper HTTP status codes and response models

5. **Register router** — Update `backend/app/api.py`
   - Import and include the new router with appropriate prefix and tags

6. **Unit tests** — `backend/tests/unit/test_${ARGUMENTS}.py`
   - Test service functions with mocked repository
   - Follow test-first skill: write tests before or alongside implementation
   - Run `make unit-test` to verify

Check existing files in each directory for reference patterns before creating new ones.
