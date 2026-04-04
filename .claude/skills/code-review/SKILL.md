---
name: code-review
description: Self-review checklist to run before considering implementation work complete. Use before finishing a feature, after all tests pass, before committing.
---

# Code Review Skill

> Adapted from [obra/superpowers-skills](https://github.com/obra/superpowers-skills) — code-reviewer standards. Customized for StrideTrack as a self-review checklist instead of subagent dispatch.

## When to Use

Run this checklist:

- Before considering a feature implementation complete
- After all tests pass but before committing
- When you've made changes across multiple files
- Before creating a pull request

## Self-Review Checklist

Go through each section. For any issue found, categorize it:

- **Critical:** Bugs, security vulnerabilities, data loss risks — fix immediately
- **Important:** Architectural problems, missing tests, type safety gaps — fix before proceeding
- **Minor:** Style issues, naming improvements — note but don't block on these

### 1. Code Quality

- [ ] Functions have clear, single responsibilities
- [ ] No duplicated logic that should be extracted
- [ ] Error handling is appropriate (not swallowed, not over-caught)
- [ ] Type annotations present on all function params and return types
- [ ] No hardcoded values that should be in config (`backend/app/core/config.py`)

### 2. Architecture (StrideTrack-specific)

- [ ] Routes only validate input and call services — no business logic
- [ ] Services contain business logic and error handling — no direct DB access
- [ ] Repositories only perform Supabase operations — no HTTP concerns
- [ ] Pydantic models used for all request/response schemas
- [ ] Frontend uses TanStack Query for data fetching (no raw fetch/useEffect)
- [ ] Frontend uses Zod for form validation

### 3. Testing

- [ ] New backend service functions have unit tests
- [ ] Bug fixes include a regression test
- [ ] Tests verify behavior, not implementation details
- [ ] `make unit-test` passes
- [ ] `make check-format` passes

### 4. Security & Production Readiness

- [ ] No secrets or credentials in code
- [ ] User input is validated before use
- [ ] No SQL injection vectors (using Supabase client properly)
- [ ] No sensitive data logged or exposed in error messages

## Issue Reporting Format

When reporting issues found during review, use:

```
[Critical/Important/Minor] file_path:line_number
Description of the issue
WHY this matters: [explanation]
```

Always explain **why** something is an issue, not just what to change.
