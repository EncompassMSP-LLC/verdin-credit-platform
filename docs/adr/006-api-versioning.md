# ADR-006: URL-Based API Versioning

**Date:** 2026-06-28  
**Authors:** Platform Team

## Status

Accepted

## Context

The platform is a long-lived enterprise SaaS product. Clients (web app, future mobile app, integrations) will need stable contracts while the API evolves. Breaking changes must be introduced without forcing all consumers to migrate on the same day.

Alternatives considered:

| Approach                             | Pros                                 | Cons                                                   |
| ------------------------------------ | ------------------------------------ | ------------------------------------------------------ |
| No versioning                        | Simple                               | Breaking changes hit all clients immediately           |
| Header versioning (`Accept-Version`) | Clean URLs                           | Harder to test, easy to miss in clients                |
| URL prefix (`/api/v1/...`)           | Explicit, cacheable, visible in logs | Longer paths; multiple versions mounted simultaneously |

We chose URL prefix versioning for clarity in OpenAPI docs, proxy rules, and client configuration.

## Decision

All public API routes are served under a versioned prefix:

```
/api/v1/<resource>
```

Version management is centralized in `api/versions/`:

- `constants.py` — `CURRENT_API_VERSION`, `SUPPORTED_API_VERSIONS`
- `registry.py` — `ApiVersion` dataclass and `mount_api_versions()` to register version routers on the FastAPI app
- `v1/router.py` — aggregates domain routers for the current release
- `v2/router.py` — reserved for future routes (empty until needed)
- `openapi.py`, `docs.py` — version-aware documentation

System endpoints:

- `GET /api/v1/health`, `GET /api/v1/version` — per-version metadata
- `GET /api/versions` — lists all registered versions and their status (`current`, `stable`, `deprecated`, `preview`)

When `v2` is introduced, both `v1` and `v2` routers mount concurrently. Deprecated versions carry `deprecated` and optional `sunset` metadata in the registry.

## Consequences

### Positive

- Clients pin to `/api/v1` and migrate to `/api/v2` on their own schedule
- OpenAPI docs and nginx proxy rules align with a single, predictable prefix
- Version discovery endpoint supports tooling and integration tests

### Negative

- Shared business logic must not assume a single API shape; breaking schema changes belong in a new version
- Multiple mounted versions increase maintenance surface during migration windows

### Neutral

- The frontend `@verdin/api-client` package uses `/api/v1` paths via `apiPath()`
- New endpoints are added to `v1` until a deliberate breaking release creates `v2`
- See [`docs/api/reference.md`](../api/reference.md) for the current endpoint catalog
