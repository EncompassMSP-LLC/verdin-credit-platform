# LRP Enterprise — Folder Structure for Cursor

How the ideal `/lrp-enterprise/` layout maps onto this monorepo. **Do not create a separate root product clone.**

```text
verdin-credit-platform/                    ← repository root (shared platform)
├── docs/lrp-enterprise/                   ← YOUR docs taxonomy (00–15)
│   ├── 00-executive/
│   ├── 01-brand/          → also see docs/brand/lending-readiness-partners/
│   ├── 02-marketing/
│   ├── 03-sales/
│   ├── 04-operations/
│   ├── 05-website/
│   ├── 06-borrower-portal/
│   ├── 07-lender-portal/
│   ├── 08-ai/
│   ├── 09-crm/
│   ├── 10-api/
│   ├── 11-legal/
│   ├── 12-compliance/
│   ├── 13-sops/
│   ├── 14-training/
│   └── 15-roadmap/
│
├── apps/
│   ├── lrp-web/                           ← website + borrower + lender + CRM UI
│   │   └── src/app/
│   │       ├── (marketing pages)          ≈ apps/website
│   │       ├── portal/                    ≈ apps/borrower-portal
│   │       ├── lender/                    ≈ apps/lender-portal
│   │       └── crm/                       ≈ apps/crm
│   ├── web/                               ≈ apps/admin (CRO staff console)
│   ├── api/                               ← system of record (all editions)
│   └── worker/                            ← async jobs (OCR, email, SMS)
│
├── packages/
│   ├── ui/                                ≈ packages/ui
│   ├── shared/ + validation/              ≈ branding tokens / shared types
│   ├── api-client/                        ≈ packages/auth + API surface for UIs
│   ├── report-parsers/                    ≈ packages/ai inputs (OCR/parse)
│   └── event-types/                       ← audit/event contracts
│
├── assets/lrp/                            ← YOUR assets tree
│   ├── logos/
│   ├── canva/
│   ├── presentations/
│   ├── brochures/
│   └── social/
│
└── .cursor/rules/lrp-enterprise-structure.mdc
```

## App mapping (ideal → actual)

| Ideal app         | Actual path    | Routes / notes                                     |
| ----------------- | -------------- | -------------------------------------------------- |
| `website`         | `apps/lrp-web` | `/`, `/lenders`, `/partners`, `/pricing`, …        |
| `borrower-portal` | `apps/lrp-web` | `/portal/*` → `/api/v1/portal/*`                   |
| `lender-portal`   | `apps/lrp-web` | `/lender/*` → `/api/v1/mortgage-partner/*` (gated) |
| `crm`             | `apps/lrp-web` | `/crm/*`                                           |
| `admin`           | `apps/web`     | Staff CRO UI → `/api/v1/*`                         |

## Package mapping (ideal → actual)

| Ideal package | Actual                                                         | Role                           |
| ------------- | -------------------------------------------------------------- | ------------------------------ |
| `ui`          | `packages/ui` + `lrp-web` components                           | Design system / edition chrome |
| `branding`    | `docs/brand/…` + `assets/lrp/logos` + `lrp-web/public/brand`   | Tokens, logos, copy            |
| `ai`          | `apps/api/api/modules/credit_analysis`, `llm`, parsers         | Advisory analysis (ADR-012)    |
| `reporting`   | `apps/api/api/modules/reporting`                               | Ops + partner analytics        |
| `auth`        | `apps/api/api/modules/auth`, `client_portal`, mortgage partner | JWT realms                     |
| `database`    | `apps/api` models + Alembic                                    | Shared Postgres multi-tenant   |

## Agent rules

1. Prefer editing `apps/lrp-web` for LRP UX; do not invent `apps/lender-web` unless UX must diverge.
2. Put durable product docs under `docs/lrp-enterprise/NN-*/`.
3. Put binary marketing assets under `assets/lrp/` (not in `apps/`).
4. Platform APIs and migrations stay in `apps/api` — never duplicated under a fork.
5. Compliance: advisory readiness only; no unsupervised bureau filing; no cross-tenant marketplace.
