# Auth realms (Epic E1)

| Field        | Value             |
| ------------ | ----------------- |
| Status       | `ready-for-build` |
| Parent       | Vol 24            |
| Last updated | 2026-07-28        |

## Realms

| Realm       | App paths    | Identity                                            | Cookie(s)                                            |
| ----------- | ------------ | --------------------------------------------------- | ---------------------------------------------------- |
| **portal**  | `/portal/*`  | Client portal JWT                                   | `lrp_portal_access` (+ refresh)                      |
| **crm**     | `/crm/*`     | Platform staff JWT `/auth/*`                        | `lrp_crm_access` (+ refresh); demo `lrp_crm_session` |
| **lender**  | `/lender/*`  | Staff JWT interim **or** demo                       | `lrp_lender_access`; demo `lrp_lender_session`       |
| **realtor** | `/realtor/*` | Staff JWT + active `partner_role=realtor` (LRP-301) | `lrp_realtor_access`; demo `lrp_realtor_session`     |

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

### Realtor (LRP-301)

| Partnership `PartnerRole` | Realtor access                                                                |
| ------------------------- | ----------------------------------------------------------------------------- |
| `realtor`                 | Own partnership session via `/mortgage-partner/realtor/me`; restricted UI nav |

Realtor users are typically `UserRole.read_only` on the partner organization. Invite accept creates membership + account; disabled membership or inactive user blocks session.

## Deferred

- Mortgage partner **member JWT** for true LO/realtor seats (`ENABLE_MORTGAGE_PARTNER` partnership members)
- SSO / MFA

## Demo fallback (LRP-108)

`NEXT_PUBLIC_LRP_CRM_DEMO_AUTH` / `NEXT_PUBLIC_LRP_LENDER_DEMO_AUTH` / `NEXT_PUBLIC_LRP_REALTOR_DEMO_AUTH` default **true** in local/dev when unset.

**Production builds always disable demo auth** (`NODE_ENV=production`), even if the flags are `true`. Stale demo cookies/localStorage are cleared on init when demo auth is off.

Platform login is attempted first; demo users apply only when demo auth is enabled, platform auth fails, and credentials match local demo tables. Realtor platform login also requires an active realtor membership (`getRealtorMe`).

## Implementation

- `apps/lrp-web/src/lib/auth/realms.ts`
- `apps/lrp-web/src/lib/auth/staff-session.ts`
- `apps/lrp-web/src/lib/crm/auth.tsx`
- `apps/lrp-web/src/lib/lender/auth.tsx`
- `apps/lrp-web/src/lib/realtor/auth.tsx`
- `apps/lrp-web/src/middleware.ts`
