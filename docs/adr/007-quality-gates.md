# ADR-007: Quality Gates (Pre-Commit and CI)

**Date:** 2026-06-28  
**Authors:** Platform Team

## Status

Accepted

## Context

The monorepo spans Python (FastAPI, worker) and TypeScript (React, shared packages). Without automated enforcement, style drift, type errors, and failing tests reach `develop` and slow down the team. Sprint 1 established a baseline toolchain; we needed a consistent gate that runs locally before commit and remotely on every pull request.

## Decision

Enforce quality through **two layers**:

### 1. Local pre-commit hooks (`.pre-commit-config.yaml`)

Run automatically on `git commit` after `pre-commit install`:

| Hook                                                     | Tool                                    | Scope                                  |
| -------------------------------------------------------- | --------------------------------------- | -------------------------------------- |
| `trailing-whitespace`, `end-of-file-fixer`, `check-yaml` | pre-commit-hooks                        | Repo-wide                              |
| `ruff` (lint + fix)                                      | Ruff                                    | `apps/api/`, `apps/worker/`            |
| `ruff-format`                                            | Ruff                                    | `apps/api/`, `apps/worker/`            |
| `mypy-api`                                               | mypy (strict, with pragmatic overrides) | `apps/api/`                            |
| `prettier`                                               | Prettier via `pnpm exec`                | `.ts`, `.tsx`, `.json`, `.md`, `.yaml` |
| `eslint`                                                 | ESLint via `pnpm exec`                  | `.ts`, `.tsx`                          |

### 2. GitHub Actions CI (`.github/workflows/ci.yml`)

Runs on push/PR to `main` and `develop`:

| Job              | Checks                                            |
| ---------------- | ------------------------------------------------- |
| `lint`           | `pnpm format:check`, `pnpm lint`                  |
| `typecheck`      | Build shared packages, `pnpm typecheck`           |
| `python-tests`   | `pytest` against PostgreSQL service, `ruff check` |
| `build-frontend` | `pnpm --filter @verdin/web build`                 |
| `build-backend`  | Verify `main:app` imports                         |
| `docker-build`   | Build API, worker, and web Docker images          |

Pull requests **must pass CI** before merge (see [`CONTRIBUTING.md`](../../CONTRIBUTING.md)).

Mypy uses strict mode with targeted overrides in `apps/api/pyproject.toml` for ORM forward references and third-party stubs.

## Consequences

### Positive

- Defects are caught before code review, reducing reviewer burden
- Consistent formatting across Python and TypeScript without manual negotiation
- CI mirrors local hooks, minimizing "works on my machine" surprises
- Docker build job validates deployable artifacts early

### Negative

- First-time setup requires `pnpm install`, Python venv, and `pre-commit install`
- Pre-commit can add latency to commits; run `pre-commit run --all-files` before large pushes
- Mypy strictness may require `pyproject.toml` overrides for legitimate framework patterns

### Neutral

- Contributors can run the same checks manually (see [`docs/developer-guide.md`](../developer-guide.md))
- New packages or apps must be added to hook `files` patterns when introduced
- Test coverage thresholds are not enforced in Sprint 1; may be added in a future ADR
