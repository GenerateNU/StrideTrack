---
name: planning
description: Structured approach to understanding requirements and planning implementation before writing code. Use when starting a new feature, significant refactor, or multi-file change.
---

# Planning Skill

> Adapted from [obra/superpowers-skills](https://github.com/obra/superpowers-skills) — brainstorming and writing-plans skills. Customized for StrideTrack with lighter enforcement and project-specific patterns.

## When to Use

- **Use full planning:** New features, multi-file changes, architectural decisions, new API endpoints
- **Skip to implementation:** Single-file fixes, config changes, styling updates, documentation edits, typo fixes

## Phase 1: Understanding

Ask clarifying questions before writing any code. One question at a time — do not overwhelm with a wall of questions.

Focus on:

- **Purpose:** What problem does this solve? Who is the user?
- **Constraints:** Performance requirements? Backward compatibility? Timeline?
- **Success criteria:** How will we know this works correctly?
- **Scope:** What is explicitly NOT in scope?

If requirements are already clear and well-scoped, acknowledge and move to Phase 2.

## Phase 2: Exploration

Present 2-3 different approaches with trade-offs. Keep each approach description to 200-300 words. Include:

- Architecture overview
- Which existing files/patterns to reuse
- Pros and cons
- Estimated complexity

For StrideTrack features, always consider:

- Does this need a new route → service → repository chain?
- Does this touch existing Supabase tables or need a migration?
- Does this affect both frontend and backend?

Get explicit approval on the chosen approach before proceeding.

## Phase 3: Planning

Break work into bite-sized tasks (2-5 minutes each). Each task must include:

- **Exact file paths** to create or modify
- **What to implement** in concrete terms
- **How to verify** (which test to write, which make command to run)

### Plan Template

```markdown
## Feature: [name]

### Goal

[One sentence describing the outcome]

### Tasks

#### 1. [Task name]

- Files: `backend/app/services/example_service.py`, `backend/tests/unit/test_example.py`
- Do: [Specific implementation details]
- Verify: `make unit-test`

#### 2. [Task name]

...
```

Plans assume the reader has zero context about the codebase. Include file paths, function names, and references to existing patterns.

## Phase 4: Execution

Implement one task at a time. After each task:

1. Run the verification step from the plan
2. If it fails, fix before moving on
3. If the plan needs adjustment based on what you learned, update it

The hooks will automatically run `make check-format` and `make unit-test` at the end of each turn.
