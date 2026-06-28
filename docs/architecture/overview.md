# Architecture

## Overview

Verdin Credit Platform v4.2 is a monorepo-based enterprise SaaS application for credit operations.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React     │────▶│   Nginx     │────▶│   FastAPI   │
│   (Vite)    │     │   Proxy     │     │   API       │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
              ┌─────▼─────┐            ┌───────▼───────┐          ┌───────▼───────┐
              │ PostgreSQL │            │    Redis      │          │    MinIO      │
              │  Database  │            │    Cache      │          │   Storage     │
              └───────────┘            └───────────────┘          └───────────────┘
                                               │
                                        ┌──────▼──────┐
                                        │   Worker    │
                                        │  (async)    │
                                        └─────────────┘
```

## Layered Backend Architecture

```
HTTP Request
    │
    ▼
Router (validation, auth deps)
    │
    ▼
Service (business logic)
    │
    ▼
Repository (database queries)
    │
    ▼
SQLAlchemy ORM → PostgreSQL
```

## Monorepo Structure

| Package | Purpose |
|---------|---------|
| `apps/api` | FastAPI backend |
| `apps/web` | React frontend |
| `apps/worker` | Background job processor |
| `packages/shared` | Shared TypeScript types |
| `packages/ui` | Shared React components |
| `packages/validation` | Shared Zod schemas |

## Key Design Decisions

- **Async SQLAlchemy** for non-blocking database access
- **JWT + Refresh tokens** for stateless authentication
- **RBAC** with 5 role levels
- **Soft delete** for all business entities
- **UUID primary keys** for distributed-friendly IDs
- **Structured JSON logging** for observability
