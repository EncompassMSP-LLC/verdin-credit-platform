# Architecture

> **Technical constitution:** See [`README.md`](README.md) for the full architecture governance index.  
> **Product direction:** See [`../roadmap/v5.0-enterprise.md`](../roadmap/v5.0-enterprise.md).

## Overview

Verdin Credit Platform is a monorepo-based enterprise SaaS application evolving from operational case management (v4.3) toward an AI-powered credit repair operations platform (v5.0).

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

| Package               | Purpose                  |
| --------------------- | ------------------------ |
| `apps/api`            | FastAPI backend          |
| `apps/web`            | React frontend           |
| `apps/worker`         | Background job processor |
| `packages/shared`     | Shared TypeScript types  |
| `packages/ui`         | Shared React components  |
| `packages/validation` | Shared Zod schemas       |

## Key Design Decisions

- **Async SQLAlchemy** for non-blocking database access
- **JWT + Refresh tokens** for stateless authentication
- **RBAC** with 5 role levels
- **Soft delete** for all business entities
- **UUID primary keys** for distributed-friendly IDs
- **Structured JSON logging** for observability

## Further reading

| Document                                          | Topic                           |
| ------------------------------------------------- | ------------------------------- |
| [System Architecture](system-architecture.md)     | Full topology and evolution     |
| [Domain Model](domain-model.md)                   | Business domains and aggregates |
| [API Standards](api-standards.md)                 | REST conventions                |
| [Security Architecture](security-architecture.md) | Auth, RBAC, audit               |
| [AI Architecture](ai-architecture.md)             | AI phases and integration       |
| [Data Model](data-model.md)                       | Persistence and lifecycles      |
| [V5.0 Roadmap](../roadmap/v5.0-enterprise.md)     | Product vision                  |
