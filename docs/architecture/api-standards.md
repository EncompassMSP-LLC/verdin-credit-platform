# API Standards

REST API conventions for all Verdin platform endpoints. Applies to `/api/v1` and future versions.

See also [ADR 006 — API versioning](../adr/006-api-versioning.md) and [API reference](../api/reference.md).

## URL structure

```
/api/{version}/{resource}
/api/{version}/{resource}/{id}
/api/{version}/{resource}/{id}/{sub-resource}
/api/{version}/{resource}/{action}   ← only when not CRUD (e.g. /accounts/intelligence/summary)
```

**Rules:**

- Plural nouns for collections: `/cases`, `/accounts`
- Kebab-case for multi-word actions: `/intelligence/summary`
- Register static path segments **before** parameterized routes (`/intelligence/summary` before `/{account_id}`)
- Nested resources under parent when scoped: `/cases/{case_id}/accounts`

## HTTP methods

| Method   | Use                                       |
| -------- | ----------------------------------------- |
| `GET`    | Read single or collection                 |
| `POST`   | Create                                    |
| `PATCH`  | Partial update                            |
| `DELETE` | Soft delete (204 No Content)              |
| `PUT`    | Avoid unless full replacement is explicit |

## Authentication

- Header: `Authorization: Bearer <access_token>`
- All business endpoints require authentication unless documented as public
- Missing/invalid token → **401 Unauthorized**
- Valid token, insufficient role → **403 Forbidden**

Public endpoints today: `/health`, `/version`, `/auth/login`, `/auth/refresh`.

## Authorization (RBAC)

Roles (lowest to highest): `read_only` → `reviewer` → `case_manager` → `admin` → `owner`

Enforce in **service layer**, not only in routers:

```python
if not has_permission(user.role, WRITE_ROLE):
    raise HTTPException(status_code=403, detail="Insufficient permissions...")
```

Document minimum role per endpoint in `docs/api/reference.md`.

## Request / response bodies

- JSON only for request/response bodies
- Pydantic schemas in `api/modules/{domain}/schemas.py`
- Shared base: `BaseSchema` from `api/core/responses.py`
- Use `Field()` for validation constraints
- UUIDs as strings in JSON; datetime as ISO 8601 UTC

### Create vs update

- **Create schema:** required fields with defaults where sensible
- **Update schema:** all fields optional (`exclude_unset=True` on apply)

## Pagination

Standard query parameters:

| Param       | Default | Max |
| ----------- | ------- | --- |
| `page`      | 1       | —   |
| `page_size` | 20      | 100 |

Response envelope (`PaginatedResponse`):

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "page_size": 20,
  "pages": 0
}
```

## Filtering and sorting

- Filters as query params matching field names: `status`, `bureau`, `case_id`
- Search: `search` param with documented searchable fields
- Sort: `sort_by` + `sort_order` (`asc` | `desc`)
- Document all supported filters in API reference

## Error responses

FastAPI standard shape:

```json
{
  "detail": "Human-readable message"
}
```

Validation errors (422) may include field-level `detail` arrays.

| Status | When                                                        |
| ------ | ----------------------------------------------------------- |
| 400    | Malformed request                                           |
| 401    | Not authenticated                                           |
| 403    | Not authorized                                              |
| 404    | Resource not found (or wrong org — do not leak existence)   |
| 409    | Conflict (duplicate case number, etc.)                      |
| 422    | Validation failure                                          |
| 500    | Unexpected server error (logged, generic message to client) |

## Versioning policy

- Breaking changes require a new API version (`/api/v2`)
- Non-breaking additions (new fields, new optional params) stay in current version
- Deprecation: document in release notes + `Sunset` header (5.0 standard)

## OpenAPI

- Auto-generated from FastAPI route definitions
- Version-scoped docs: `/api/v1/docs`
- Keep `response_model` on all endpoints for schema accuracy

## Frontend client (`@verdin/api-client`)

Every new endpoint requires:

1. Typed interface in `packages/api-client/src/{domain}.ts`
2. Export from `packages/api-client/src/index.ts`
3. Shared enums in `@verdin/shared` when reused by UI

Use `request()` helper — do not duplicate fetch logic in `apps/web`.

## Module implementation checklist

1. `schemas.py` — Create, Update, Response, ListParams
2. `repository.py` — all SQLAlchemy
3. `service.py` — business logic + RBAC
4. `router.py` — thin HTTP layer
5. `permissions.py` — role constants
6. Register in `api/versions/v1/router.py`
7. Tests in `tests/{domain}/`
8. Update `docs/api/reference.md`

## Performance target

p95 latency **< 250 ms** for standard CRUD and list operations at expected load (see [roadmap success metrics](../roadmap/v5.0-enterprise.md#success-metrics)).

List endpoints must use indexed filters and limit `page_size` to prevent unbounded queries.
