# 06 — Borrower Portal

Consumer experience for mortgage-intent borrowers.

## Code

| Layer  | Path                                  |
| ------ | ------------------------------------- |
| UI     | `apps/lrp-web/src/app/portal/`        |
| API    | `apps/api/api/modules/client_portal/` |
| Client | `packages/api-client` portal helpers  |

## Flag

`ENABLE_CLIENT_PORTAL=true`

## Guardrails

Advisory readiness / insights only — not credit decisions or funding guarantees. Staff provisions portal users (no open self-serve signup by default).
