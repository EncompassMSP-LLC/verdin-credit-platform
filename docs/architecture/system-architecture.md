# System Architecture

High-level design for the Verdin Credit Platform from v4.2 foundation through v5.0 Enterprise.

## Platform topology

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           Client layer                                    │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐ (planned 4.8+)     │
│  │  Staff Web  │   │ Mobile Web  │   │Client Portal│                     │
│  │  (React)    │   │ (responsive)│   │             │                     │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘                     │
└─────────┼─────────────────┼─────────────────┼────────────────────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ▼
                   ┌────────────────┐
                   │  Nginx / CDN   │  TLS termination, static assets
                   └────────┬───────┘
                            ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         Application layer                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    FastAPI API (`apps/api`)                          │ │
│  │  /api/v1/*  — versioned REST modules (auth, cases, accounts, …)     │ │
│  └───────────────────────────────┬─────────────────────────────────────┘ │
│                                  │ enqueue (4.5+)                        │
│  ┌───────────────────────────────▼─────────────────────────────────────┐ │
│  │              Worker (`apps/worker`) — Redis queue                    │ │
│  │  OCR, imports, AI summaries, notifications, workflow steps         │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┬─────────────────┐
          ▼                 ▼                 ▼                 ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │ PostgreSQL  │   │    Redis    │   │   MinIO     │   │ External    │
   │ (primary)   │   │ cache/queue │   │  (objects)  │   │ APIs (5.0)  │
   └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘
```

## Architectural style

| Layer          | Responsibility                                             |
| -------------- | ---------------------------------------------------------- |
| **Router**     | HTTP concerns: validation, auth dependencies, status codes |
| **Service**    | Business logic, permissions, orchestration, intelligence   |
| **Repository** | Database access only — SQLAlchemy queries                  |
| **Model**      | SQLAlchemy ORM entities                                    |
| **Worker job** | Async, idempotent side effects (OCR, email, imports)       |

Routers **must not** import SQLAlchemy sessions for queries directly. See [ADR 005](../adr/005-domain-modules.md).

## Monorepo layout

| Path                  | Role                                  |
| --------------------- | ------------------------------------- |
| `apps/api`            | FastAPI backend, Alembic migrations   |
| `apps/web`            | React + Vite staff application        |
| `apps/worker`         | Background job processor              |
| `packages/shared`     | Cross-app TypeScript types and labels |
| `packages/ui`         | Design system components              |
| `packages/validation` | Zod schemas shared by web and tooling |
| `packages/api-client` | Typed HTTP client for the API         |

Build orchestration: **pnpm workspaces** + **Turborepo**.

## API versioning

All business endpoints live under `/api/v1`. Version discovery and combined OpenAPI are at `/api/versions` and `/docs`. See [ADR 006](../adr/006-api-versioning.md) and [API Standards](api-standards.md).

## Event-driven evolution (4.3 → 5.0)

Today, domain modules write directly to PostgreSQL. The target architecture adds an **event emission** step in services:

```
Service action → persist entity → emit domain event → Timeline / Workflow / Analytics consumers
```

Timeline events (`TimelineEvent`) are the first consumer. Workflow automation (4.5) and immutable audit (5.0) subscribe to the same event stream pattern.

## Multi-tenancy model

- **Tenant key:** `organization_id` on all business entities
- **User membership:** Each user belongs to one organization (5.0 may add cross-org admin roles)
- **Query scoping:** Every repository list/get filters by caller's organization
- **RBAC:** Role hierarchy enforced in services via `has_permission()`

## Deployment (cloud-native)

- **Containers:** API, web, worker, PostgreSQL, Redis, MinIO via Docker Compose (dev) and orchestrated production (Kubernetes or managed services — TBD)
- **Stateless API:** JWT access tokens; refresh tokens with rotation
- **Horizontal scaling:** API and worker replicas behind load balancer; Redis for queue; PostgreSQL primary

## Cross-cutting concerns

| Concern       | Implementation                                                       |
| ------------- | -------------------------------------------------------------------- |
| Logging       | Structured JSON (`api/core/logging`)                                 |
| Audit fields  | `created_by_id`, `updated_by_id`, timestamps                         |
| Soft delete   | `deleted_at` on business entities                                    |
| Feature flags | `ENABLE_*` env vars (API + web)                                      |
| Quality gates | Pre-commit + GitHub Actions ([ADR 007](../adr/007-quality-gates.md)) |

## Evolution path to 5.0 Enterprise

| Phase   | Architectural change                                                |
| ------- | ------------------------------------------------------------------- |
| **4.3** | Complete operational domains; timeline event emission standard      |
| **4.5** | Worker-heavy import/OCR/AI; workflow engine module                  |
| **4.8** | Read-optimized reporting views; client portal auth partition        |
| **5.0** | Compliance center, SSO, enterprise audit store, integration gateway |

See [Version 5.0 Enterprise Roadmap](../roadmap/v5.0-enterprise.md) for domain-level detail.
