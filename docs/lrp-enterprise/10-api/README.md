# 10 — API

Platform and partner API surfaces used by LRP apps.

## Primary references

- [API reference](../../api/reference.md) — especially **Mortgage Partner Edition** and **Client portal**
- OpenAPI: `/docs` on the API service
- Typed client: `packages/api-client`

## Key prefixes

| Prefix                       | Audience                                            |
| ---------------------------- | --------------------------------------------------- |
| `/api/v1/portal/*`           | Borrowers                                           |
| `/api/v1/mortgage-partner/*` | CRO staff managing partnerships (partner JWT later) |
| `/api/v1/clients             | cases                                               | tasks | documents | notifications/*` | Staff / CRM wiring |

## Flags

`ENABLE_CLIENT_PORTAL` · `ENABLE_MORTGAGE_PARTNER`
