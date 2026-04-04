# Claude Code Setup Guide for StrideTrack

This guide explains how Claude Code is configured in this repository and how to use it effectively.

## Prerequisites

Make sure you have these installed (same as normal development):

- **Node.js** — required for cross-platform hooks
- **uv** — Python package manager (backend)
- **Bun** — JavaScript runtime and package manager (frontend)
- **Python 3.13.9** — backend runtime

Run `make check-deps` to verify everything is installed.

## What's Configured

### Automatic Hooks

Hooks run automatically — no setup required. They're defined in `.claude/settings.json`.

| When | What Runs | Purpose |
|------|-----------|---------|
| After every file edit | `make format-backend` or `make format-frontend` | Auto-fixes formatting for the file you just changed |
| End of every turn | `make check-format` | Verifies all linting and formatting passes |
| End of every turn | `make unit-test` | Runs backend unit tests to catch regressions |

If a hook fails, Claude sees the failure output and will attempt to fix the issue.

### Permissions

These commands are **auto-approved** (Claude can run without asking):
- `make check-format`, `make format`, `make unit-test`
- `bun install`, `uv run`, `bun run`

These commands are **blocked** (Claude cannot run):
- `git push`
- `make db-migrate`
- `make clean`

Everything else (including `git commit`) requires your approval.

### Custom Skills

Skills are prompting strategies that activate based on the task at hand. They live in `.claude/skills/`.

| Skill | When It Activates | What It Does |
|-------|-------------------|--------------|
| **Planning** | New features, multi-file changes | Asks clarifying questions, explores approaches, breaks work into tasks |
| **Test-First** | New service functions, bug fixes | Encourages writing tests before implementation (red-green-refactor) |
| **Code Review** | Before finishing work | Self-review checklist for quality, architecture, and testing |
| **Debugging** | Errors, test failures | Structured root cause investigation before applying fixes |

Skills are guidelines, not hard blockers. They're adapted from the [Superpowers](https://github.com/obra/superpowers-skills) framework with lighter enforcement.

### Slash Commands

| Command | Usage | Purpose |
|---------|-------|---------|
| `/fix-lint` | `/fix-lint` | Auto-fix all linting and formatting issues |
| `/add-endpoint` | `/add-endpoint athlete` | Scaffold a new backend endpoint (route + service + repo + tests) |
| `/add-component` | `/add-component WorkoutCard` | Scaffold a new React component following conventions |

### Rules

Rules in `.claude/rules/` are auto-loaded into every conversation:
- `backend.md` — Python/FastAPI coding standards
- `frontend.md` — React/TypeScript conventions
- `testing.md` — Testing requirements and locations

## Personal Customization

To override settings for your local environment, edit `.claude/settings.local.json` (gitignored).

Example — adding MCP server permissions:

```json
{
  "permissions": {
    "allow": [
      "mcp__my_tool__my_action"
    ]
  }
}
```

Your local settings merge with the team settings. You cannot override team `deny` rules.

## Troubleshooting

### Hook fails with "command not found"

Make sure `uv`, `bun`, and `node` are installed and on your PATH. Run `make check-deps` to verify.

### Format hook fails on frontend

Run `cd frontend && bun install` first. The formatter needs `node_modules` to be present.

### Unit tests fail on hook

The Stop hook runs `make unit-test` after every turn. If tests are failing for reasons unrelated to your current work, you can temporarily disable the hook in `.claude/settings.local.json`:

```json
{
  "hooks": {
    "Stop": []
  }
}
```

### MCP servers not working

MCP configuration (`.mcp.json`) is gitignored because it references locally-installed tools. Each developer sets up their own MCP servers.

## File Structure

```
.claude/
├── settings.json          # Team config: hooks, permissions (committed)
├── settings.local.json    # Personal overrides (gitignored)
├── hooks/
│   └── format-edited.mjs  # Cross-platform format hook (Node.js)
├── skills/
│   ├── planning/SKILL.md
│   ├── test-first/SKILL.md
│   ├── code-review/SKILL.md
│   └── debugging/SKILL.md
├── commands/
│   ├── fix-lint.md
│   ├── add-endpoint.md
│   └── add-component.md
└── rules/
    ├── backend.md
    ├── frontend.md
    └── testing.md
```
