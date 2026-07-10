# Ultimate Credit Repair LLC — Agent Instructions

> Version 4.2.0 | Sprint 1 Platform Foundation

This document defines roles, responsibilities, coding standards, and architectural rules for AI-assisted development on Ultimate Credit Repair LLC.

## Project Overview

Ultimate Credit Repair LLC is an enterprise SaaS application for credit operations: case management, document intelligence, automation, analytics, and AI-assisted workflows.

**Stack:** pnpm monorepo · Turborepo · FastAPI · React · PostgreSQL · Redis · MinIO · Docker

## Agent Roles

### Backend Engineer

**Scope:** `apps/api/`, `apps/worker/`

**Responsibilities:**

- Implement FastAPI routers, services, repositories, and schemas
- Write Alembic migrations for all schema changes
- Implement JWT authentication and RBAC
- Write pytest tests for every endpoint
- Maintain OpenAPI documentation accuracy

**Rules:**

- Routers never access SQLAlchemy directly
- All business logic belongs in services
- Repositories own database access
- Never duplicate database logic
- Use pydantic-settings for configuration
- Use structured logging (structlog)

### Frontend Engineer

**Scope:** `apps/web/`, `packages/ui/`

**Responsibilities:**

- Build React pages and components with TypeScript
- Use TanStack Query for server state
- Use React Hook Form + Zod for forms
- Implement authentication flows
- Maintain responsive, accessible UI

**Rules:**

- Shared types live in `@verdin/shared`
- Validation schemas live in `@verdin/validation`
- Reusable UI components live in `@verdin/ui`
- No inline API URL hardcoding — use environment variables
- All authenticated routes must use `ProtectedRoute`

### Database Engineer

**Scope:** `apps/api/api/models/`, `apps/api/alembic/`, `infrastructure/postgres/`

**Responsibilities:**

- Design and maintain SQLAlchemy models
- Create Alembic migrations for every schema change
- Maintain seed scripts
- Document ERD and schema decisions

**Rules:**

- UUID primary keys on all entities
- UTC timestamps (`DateTime(timezone=True)`)
- Soft delete via `deleted_at`
- Audit fields: `created_by_id`, `updated_by_id`
- Always create migrations — never modify production schema manually

### AI Engineer

**Scope:** Future `apps/ai/`, worker tasks, document processing

**Responsibilities:**

- Design AI pipeline integrations
- Implement document OCR and classification
- Build embedding and retrieval systems
- Ensure AI features are auditable

**Rules:**

- AI outputs must be traceable (model, version, timestamp)
- Never send PII to external APIs without explicit configuration
- All AI endpoints require authentication and appropriate RBAC

### QA Engineer

**Scope:** `tests/`, `apps/api/tests/`, CI workflows

**Responsibilities:**

- Write and maintain test suites
- Ensure CI passes on every PR
- Define test plans for new features
- Monitor test coverage

**Rules:**

- Every endpoint must have tests
- Test both success and failure paths
- Integration tests use TestClient
- No merging with failing CI

### Documentation Engineer

**Scope:** `docs/`, `README.md`, `AGENTS.md`, release notes

**Responsibilities:**

- Maintain architecture documentation
- Update API docs when endpoints change
- Write ADRs for significant decisions
- Keep developer guide current

**Rules:**

- Every feature updates documentation
- Document breaking changes in release notes
- Keep ERD in sync with models

## Architectural Rules

1. **Layered architecture:** Router → Service → Repository → Database
2. **Authentication:** All endpoints require auth unless explicitly public
3. **RBAC roles:** Owner > Admin > Case Manager > Reviewer > Read Only
4. **No secrets in code:** Use environment variables
5. **UUID keys everywhere**
6. **UTC timestamps everywhere**
7. **Soft delete by default** for business entities
8. **Monorepo packages** for shared code — no copy-paste between apps

## Coding Standards

### Python (Backend)

- Python 3.13+
- Type hints on all functions
- Pydantic v2 for schemas
- SQLAlchemy 2.x async patterns
- Ruff for linting
- 100 character line length

### TypeScript (Frontend)

- Strict mode enabled
- Functional components with hooks
- Zod for runtime validation
- Tailwind for styling
- ESLint + Prettier

### Git

- Conventional commit messages
- Feature branches from `develop`
- PRs require CI pass
- No force push to `main`

## Review Requirements

Before merging any PR:

- [ ] CI pipeline passes (lint, typecheck, tests, build)
- [ ] New endpoints have tests
- [ ] Schema changes have Alembic migrations
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] RBAC applied to protected endpoints
- [ ] Follows layered architecture

## Testing Expectations

| Layer         | Tool                   | Coverage Target |
| ------------- | ---------------------- | --------------- |
| API endpoints | pytest + TestClient    | Every endpoint  |
| Services      | pytest (unit)          | Critical paths  |
| Frontend      | Vitest (Sprint 2+)     | Key flows       |
| E2E           | Playwright (Sprint 3+) | Auth + CRUD     |

## Directory Reference

```
apps/api/api/
  core/         # Shared utilities (config, security, permissions, pagination, audit, exceptions, responses)
  modules/      # Domain modules (auth, cases, accounts, documents, tasks, timeline, ...)
    <domain>/   # router, service, repository, schemas, models
  database/     # Engine, session, declarative base
  middleware/   # Request logging, etc.

apps/web/src/
  pages/        # Route pages
  components/   # UI components
  lib/          # API client, auth
  routes/       # React Router config

packages/
  shared/       # Shared TypeScript types
  ui/           # Shared React components
  validation/   # Shared Zod schemas
```

## Getting Started

```bash
# Install dependencies
pnpm install

# Copy environment
cp .env.example .env

# Start full stack
docker compose up

# Or run locally
pnpm dev                    # All apps
cd apps/api && uvicorn main:app --reload
cd apps/web && pnpm dev
```

## Agent Sprint Loop (Version 4.5)

For hands-off dispute-generation slices (auto-merge + continue after merge), see [`docs/development/agent-sprint-loop.md`](docs/development/agent-sprint-loop.md) and `.cursor/rules/version-45-sprint-loop.mdc`.

## Demo Credentials (after seed)

| Email             | Password    | Role  |
| ----------------- | ----------- | ----- |
| owner@verdin.demo | changeme123 | Owner |
| admin@verdin.demo | changeme123 | Admin |
