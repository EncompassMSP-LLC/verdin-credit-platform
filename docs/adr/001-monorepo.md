# Architecture Decision Records

## ADR-001: Monorepo with pnpm and Turborepo

**Status:** Accepted

Use pnpm workspaces with Turborepo for build orchestration. Shared packages (`shared`, `ui`, `validation`) enable type-safe code sharing between frontend apps without duplication.

## ADR-002: Layered Backend Architecture

**Status:** Accepted

Enforce Router → Service → Repository → Database layering. Routers handle HTTP concerns only. Services contain business logic. Repositories own all SQLAlchemy access.

## ADR-003: UUID Primary Keys

**Status:** Accepted

All entities use UUID v4 primary keys for distributed-system compatibility and to avoid enumeration attacks.

## ADR-004: JWT with Refresh Tokens

**Status:** Accepted

Stateless JWT authentication with short-lived access tokens (30 min) and longer-lived refresh tokens (7 days). Enables horizontal scaling without session stores.
