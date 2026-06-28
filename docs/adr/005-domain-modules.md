# ADR-005: Domain-Driven API Modules

**Date:** 2026-06-28  
**Authors:** Platform Team

## Status

Accepted

## Context

The initial FastAPI backend used a layer-first layout (`routers/`, `services/`, `repositories/` at the application root). As domains grew (auth, cases, accounts, documents, tasks, imports, analytics, timeline), cross-cutting changes required touching many unrelated directories. Ownership boundaries were unclear, and new endpoints were hard to locate.

We needed a structure that:

- Groups code by business domain
- Preserves the Router → Service → Repository layering inside each domain
- Shares cross-cutting utilities without duplicating them per module
- Supports incremental delivery (Sprint 1 auth only; other domains scaffolded for Sprint 2)

## Decision

Organize the API under `apps/api/api/modules/<domain>/`, with one folder per bounded context:

```
api/modules/<domain>/
  router.py       # HTTP endpoints, request/response models
  service.py      # Business logic
  repository.py   # SQLAlchemy data access (when implemented)
  schemas.py      # Pydantic request/response schemas
  models.py       # SQLAlchemy ORM models
```

Shared, domain-agnostic utilities live in `api/core/` (config, security, pagination, permissions, exceptions, audit mixins, responses).

Repository **interfaces** are defined as Python `Protocol`s in `api/repositories/` (e.g. `UserRepositoryProtocol`). Concrete repositories in domain modules implement these protocols structurally. Services depend on protocols where possible to enable testing and future swapping.

Domain routers are registered through the API version layer (`api/versions/v1/`), not mounted individually in `main.py`.

Current domains: `auth`, `cases`, `accounts`, `documents`, `tasks`, `imports`, `analytics`, `timeline`.

## Consequences

### Positive

- Developers can find all code for a feature in one directory
- Domains can be owned by different engineers with minimal merge conflicts
- Shared `api/core/` prevents duplication of security, pagination, and response patterns
- Protocol-based repositories prepare for unit testing without a database

### Negative

- Some imports cross domain boundaries (e.g. `User` referenced from `cases` models); relationship direction must be managed carefully
- Domains without endpoints yet still carry models/schemas, which can look "incomplete" until Sprint 2

### Neutral

- New domains follow the same folder layout and register routers in `api/versions/v1/router.py`
- Layering rules from ADR-002 still apply inside each module; routers must not query the database directly
- See [`docs/developer-guide.md`](../developer-guide.md) for the endpoint creation checklist
