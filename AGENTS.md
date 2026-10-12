# Agent Instructions

Context for AI coding assistants (Claude Code, Cursor, Copilot, Codex).

## Project
SEO Page Checker: a small FastAPI service that analyzes the HTML of a page and returns an
on-page SEO report (score, grade, per-rule findings). Production-bound; other engineers will
continue it, so keep code readable and tested.

## Stack
Python 3.12, FastAPI, pydantic, stdlib `html.parser` (no extra parsing deps), pytest, ruff,
Docker, GitHub Actions.

## Layout
- `app/config.py`   environment configuration
- `app/models.py`   pydantic request/response schemas
- `app/analyzer.py` HTML parsing + SEO rules (pure functions, no I/O)
- `app/main.py`     thin HTTP layer
- `tests/`          pytest tests (no network)

## Commands
`make install` | `make run` | `make test` | `make lint` | `make docker-up`

## Rules
- Business logic lives in `analyzer.py`; `main.py` stays thin.
- Every rule has id, description, severity, weight. Weights must sum to 100 (a test enforces it).
- Adding a rule = check function + Rule entry + pass AND fail tests + README rules table update.
- Tests must not touch the network. No new dependency without a note in docs/ARCHITECTURE.md.
- Config via environment variables; never hardcode secrets.
- Run `make lint test` after every step.

## Out of scope
Fetching pages by URL (SSRF risk), authentication, UI, JavaScript rendering.
