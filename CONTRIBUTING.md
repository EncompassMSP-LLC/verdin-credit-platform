# Contributing to Verdin Credit Platform

Thank you for contributing. This document defines our Git workflow and commit message standard so changes stay traceable to Sprints and Epics.

## Branch Strategy

| Branch                     | Purpose                                   |
| -------------------------- | ----------------------------------------- |
| `main`                     | Production-ready releases                 |
| `develop`                  | Integration branch for active sprint work |
| `feature/*`, `fix/*`, etc. | Short-lived topic branches                |

**Always branch from `develop`** unless you are preparing a hotfix for `main`.

### Branch Naming

Use lowercase, hyphen-separated names with a type prefix:

```
<type>/<short-description>
```

| Prefix      | Use when                                   |
| ----------- | ------------------------------------------ |
| `feature/`  | New functionality                          |
| `fix/`      | Bug fixes                                  |
| `refactor/` | Code restructuring without behavior change |
| `docs/`     | Documentation only                         |
| `test/`     | Test additions or fixes                    |
| `ci/`       | CI/CD pipeline changes                     |
| `chore/`    | Tooling, dependencies, housekeeping        |

**Examples**

```
feature/sprint-2-case-list-api
fix/auth-refresh-token-expiry
refactor/domain-module-structure
docs/api-versioning-guide
ci/add-python-3-13-matrix
```

For sprint work, include the sprint number in the branch name when practical:

```
feature/sprint-2-import-pipeline
```

## Pull Request Workflow

1. **Create a branch** from `develop` using the naming convention above.
2. **Make focused commits** following [Conventional Commits](#conventional-commits) (one logical change per commit).
3. **Push** your branch and open a PR targeting `develop`.
4. **Fill out the PR template** — every PR must reference the Sprint and Epic (see below).
5. **Ensure CI passes** — lint, typecheck, tests, and builds must be green.
6. **Request review** from at least one team member (two for architectural changes).
7. **Address feedback** with new commits; avoid force-pushing after review unless rebasing is agreed.
8. **Squash or merge** per reviewer preference once approved.

### PR Requirements

Every pull request **must** include:

- **Sprint reference** — e.g. `Sprint 2 — Data Platform`
- **Epic reference** — e.g. `Epic 3 — Import & OCR`
- **Summary** of what changed and why
- **Test plan** — steps to verify the change

**PR title format** (recommended):

```
[Sprint N][Epic M] <short description>
```

**Example PR title**

```
[Sprint 2][Epic 4] Add case list endpoint with pagination
```

**Example PR description**

```markdown
## Sprint / Epic

- **Sprint:** Sprint 2 — Data Platform
- **Epic:** Epic 4 — Case Management API

## Summary

Adds `GET /api/v1/cases` with cursor pagination and RBAC for Case Manager role.

## Test plan

- [ ] `pytest apps/api/tests/test_cases.py` passes
- [ ] Manual test: login as `admin@verdin.demo`, fetch cases list
- [ ] OpenAPI updated at `/api/v1/docs`
```

### Review Checklist

Before approving a PR, confirm:

- [ ] CI pipeline passes
- [ ] Sprint and Epic are referenced
- [ ] Conventional Commit messages are used
- [ ] Tests cover new behavior
- [ ] Documentation updated when behavior or APIs change
- [ ] No secrets or credentials committed
- [ ] Alembic migration included for schema changes

## Conventional Commits

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

### Format

```
<type>(<optional scope>): <description>

[optional body]

[optional footer(s)]
```

- **type** — required; see table below
- **scope** — optional; module or area affected (e.g. `api`, `web`, `auth`, `docker`)
- **description** — imperative mood, lowercase, no trailing period
- **body** — optional; explain motivation and contrast with previous behavior
- **footer** — optional; e.g. `Refs: Sprint 2 / Epic 4`

### Commit Types

| Type       | When to use                                             |
| ---------- | ------------------------------------------------------- |
| `feat`     | New feature or user-facing capability                   |
| `fix`      | Bug fix                                                 |
| `docs`     | Documentation only                                      |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test`     | Adding or correcting tests                              |
| `ci`       | CI/CD configuration and scripts                         |
| `build`    | Build system, dependencies, or packaging                |
| `perf`     | Performance improvement                                 |
| `chore`    | Maintenance that doesn't fit other types                |

### Examples

```bash
# Feature
feat(api): add case list endpoint with pagination

# Bug fix
fix(auth): reject expired refresh tokens

# Documentation
docs: add API versioning section to reference

# Refactor
refactor(api): move auth logic into domain module

# Tests
test(api): add versioning discovery endpoint tests

# CI
ci: run ruff and pytest on pull request

# Build
build(docker): pin PostgreSQL image to 16-alpine

# Performance
perf(api): add index on cases.organization_id

# Chore
chore: update pnpm lockfile

# With scope and sprint/epic footer
feat(web): add cases page shell

Implements read-only case list UI for Sprint 2.

Refs: Sprint 2 / Epic 7
```

### Breaking Changes

Append `!` after the type/scope or add a `BREAKING CHANGE:` footer:

```
feat(api)!: rename /cases to /credit-cases

BREAKING CHANGE: Case collection path changed from /cases to /credit-cases.
Clients must update API calls.
```

## Local Development

See [docs/developer-guide.md](docs/developer-guide.md) for setup instructions.

Quick checks before pushing:

```bash
pnpm lint && pnpm typecheck
cd apps/api && ruff check . && pytest
```

## Questions

For architecture decisions, see [docs/adr/](docs/adr/) and [AGENTS.md](AGENTS.md).

For coding standards, see [docs/coding-standards.md](docs/coding-standards.md).
