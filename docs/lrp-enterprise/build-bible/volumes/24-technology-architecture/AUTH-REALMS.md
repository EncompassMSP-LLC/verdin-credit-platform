# Auth realms (Epic E1)

| Field        | Value             |
| ------------ | ----------------- |
| Status       | `ready-for-build` |
| Parent       | Vol 24            |
| Last updated | 2026-07-22        |

## Realms

| Realm      | App paths   | Identity                      | Cookie(s)                                            |
| ---------- | ----------- | ----------------------------- | ---------------------------------------------------- |
| **portal** | `/portal/*` | Client portal JWT             | `lrp_portal_access` (+ refresh)                      |
| **crm**    | `/crm/*`    | Platform staff JWT `/auth/*`  | `lrp_crm_access` (+ refresh); demo `lrp_crm_session` |
| **lender** | `/lender/*` | Staff JWT interim **or** demo | `lrp_lender_access`; demo `lrp_lender_session`       |

## Role mapping (staff → edition)

### CRM

| Platform `UserRole` | CRM role          |
| ------------------- | ----------------- |
| owner / admin       | `crm_admin`       |
| case_manager        | `ops_coordinator` |
| reviewer            | `loan_officer`    |
| read_only           | `read_only`       |

### Lender (interim)

| Platform `UserRole` | Lender role        |
| ------------------- | ------------------ |
| owner / admin       | `lender_admin`     |
| case_manager        | `credit_ops`       |
| reviewer            | `underwriter_view` |
| read_only           | `read_only`        |

## Deferred

- Mortgage partner **member JWT** for true LO/realtor seats (`ENABLE_MORTGAGE_PARTNER` partnership members)
- SSO / MFA

## Demo fallback

`NEXT_PUBLIC_LRP_CRM_DEMO_AUTH` / `NEXT_PUBLIC_LRP_LENDER_DEMO_AUTH` default **true**. Platform login is attempted first; demo users apply when platform auth fails and credentials match local demo tables.

## Implementation

- `apps/lrp-web/src/lib/auth/realms.ts`
- `apps/lrp-web/src/lib/auth/staff-session.ts`
- `apps/lrp-web/src/lib/crm/auth.tsx`
- `apps/lrp-web/src/lib/lender/auth.tsx`
- `apps/lrp-web/src/middleware.ts`
