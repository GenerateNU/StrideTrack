---
name: test-first
description: Write tests before implementation for new backend logic, following red-green-refactor methodology. Use when creating new service functions, repository methods, or fixing bugs.
---

# Test-First Development Skill

> Adapted from [obra/superpowers-skills](https://github.com/obra/superpowers-skills) — test-driven-development and testing-anti-patterns skills. Customized for StrideTrack with scope-based enforcement (not universal TDD) and no code deletion.

## Scope-Based Enforcement

### Required TDD (write tests FIRST)
- New backend service functions (`backend/app/services/`)
- New repository methods (`backend/app/repositories/`)
- Bug fixes (reproduce the bug as a failing test first)
- New utility functions (`backend/app/core/`)

### Tests Encouraged (write tests, but implementation-first is OK)
- Frontend components and hooks
- API route handlers (`backend/app/routes/`)
- Complex UI interactions

### No TDD Needed
- Config files, environment setup
- Styling and CSS changes
- Documentation and README updates
- Database migrations
- Simple one-line fixes where the change is obvious

## The Red-Green-Refactor Cycle

For tasks requiring TDD:

### 1. RED — Write a Failing Test

Write one focused test per behavior. The test should:
- Test a single, specific behavior
- Have a descriptive name explaining what it verifies
- Use arrange-act-assert structure
- Live in `backend/tests/unit/` (no Supabase needed) or `backend/tests/integration/`

Run `make unit-test` and **verify the test fails**. If it passes without implementation, the test is not testing the right thing.

### 2. GREEN — Write Minimal Implementation

Write the **simplest code** that makes the test pass. No more, no less.
- Do not add features the test does not require
- Do not optimize prematurely
- YAGNI — You Aren't Gonna Need It

Run `make unit-test` and verify the test passes.

### 3. REFACTOR — Clean Up

With passing tests as your safety net:
- Remove duplication
- Improve naming
- Simplify logic
- Ensure the code follows StrideTrack patterns (route → service → repository)

Run `make unit-test` again to verify nothing broke.

## For Bug Fixes

1. **Write a failing test** that reproduces the exact bug
2. Verify the test fails in the way the bug manifests
3. Implement the minimal fix
4. Verify the test passes
5. Check that no existing tests broke

## If You Wrote Code Before Tests

If you find yourself with implementation but no tests: **pause**. Write the tests now before proceeding to the next task. Do not move on until tests exist for the new logic.

## Testing Anti-Patterns to Avoid

These patterns create tests that pass but don't actually verify correct behavior:

### Never Test Mock Behavior
- **Wrong:** Assert that a mock was called with specific arguments
- **Right:** Test that the actual function produces the correct output given specific input

### Never Add Test-Only Methods to Production Code
- **Wrong:** Adding a `get_internal_state()` method just for test assertions
- **Right:** Test through the public API; use test utilities for setup

### Never Mock Without Understanding Dependencies
- **Wrong:** Mock everything the function touches to isolate it
- **Right:** Understand what the function actually depends on; mock only external boundaries (Supabase client, external APIs)

## StrideTrack Test Conventions

- Unit tests: `backend/tests/unit/test_{feature}.py`
- Integration tests: `backend/tests/integration/test_{feature}.py`
- Run unit tests: `make unit-test` (fast, no Supabase)
- Run integration tests: `make int-test` (requires `make up`)
- Run all: `make test`
