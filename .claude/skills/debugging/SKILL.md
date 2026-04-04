---
name: systematic-debugging
description: Structured approach to finding and fixing bugs through root cause investigation before applying fixes. Use when encountering errors, test failures, or unexpected behavior.
---

# Systematic Debugging Skill

> Adapted from [obra/superpowers-skills](https://github.com/obra/superpowers-skills) — systematic-debugging and root-cause-tracing skills. Customized for StrideTrack with lighter enforcement while keeping the core methodology.

## Core Principle

**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**

When the root cause is obvious and the fix is clearly correct, a quick fix is fine. But when the cause is unclear, or a fix attempt has already failed, follow the structured process below.

## When to Use the Full Process

- Error you haven't seen before
- Test failing for unclear reasons
- A "quick fix" didn't work
- Multiple related failures
- Intermittent/flaky behavior

## Phase 1: Root Cause Investigation

Before writing any fix:

1. **Read the full error** — stack trace, error message, file and line number
2. **Reproduce consistently** — find the exact steps or test that triggers it
3. **Check recent changes** — what was modified since this last worked? (`git diff`, `git log`)
4. **Gather evidence** — add temporary logging, check variable values, trace data flow
5. **Trace backward** — follow the error back through the call chain to find the original trigger

### Tracing Backward

Start at the symptom and ask "what called this?" repeatedly:

- Symptom → immediate cause → what called this → what provided bad data → **root cause**

Don't stop at the first thing that looks wrong. Keep tracing until you find where the incorrect state was **first introduced**.

## Phase 2: Pattern Analysis

- Find a working example of similar code in the codebase
- Compare the working and broken versions systematically
- Identify the specific difference that causes the failure
- Check if the same pattern appears elsewhere (might be multiple instances of the same bug)

## Phase 3: Hypothesis and Testing

- Form a specific hypothesis: "The bug is caused by X because Y"
- Test one variable at a time — don't make multiple changes simultaneously
- Verify your hypothesis before writing the fix

## Phase 4: Implementation

1. **Write a failing test** that reproduces the bug (test-first skill)
2. **Implement the minimal fix** — change as little as possible
3. **Verify the fix** — run `make unit-test` and any related tests
4. **Check for collateral damage** — did the fix break anything else?

## Escalation Rule

**After 3+ failed fix attempts:** Stop. Step back and evaluate:

- Is the architecture itself flawed?
- Are you fixing the wrong layer? (route vs service vs repository)
- Do you need to understand more context before proceeding?
- Should you ask the user for clarification?

Do not keep applying patches to the same area. If three attempts haven't worked, the problem is likely different from what you think.

## Red Flags

Watch for these signs that you're skipping investigation:

- "Let me just try..." without understanding the cause
- Making multiple changes at once
- Fixing a symptom rather than the root cause
- "It works now" without understanding why
