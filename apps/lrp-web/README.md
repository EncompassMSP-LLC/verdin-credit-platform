# Lending Readiness Partners — Web & Borrower Portal

Marketing site + Borrower Portal wired to the **shared Ultimate Credit Repair / Verdin platform API and Postgres**.

**Enterprise architecture:** [`docs/architecture/lending-readiness-partners.md`](../../docs/architecture/lending-readiness-partners.md)  
**Implementation phases:** [`docs/development/lrp-enterprise-implementation-phases.md`](../../docs/development/lrp-enterprise-implementation-phases.md)

## Stack

- Next.js 15 · TypeScript · Tailwind · Framer Motion
- `@verdin/api-client` → platform `/portal/*` APIs
- Portal JWT auth (same `client_portal_users` table as staff-provisioned client portal)
- next-themes · TanStack Query · lucide-react

## Platform wiring

| Concern     | Source                                                                     |
| ----------- | -------------------------------------------------------------------------- |
| Auth        | `POST /api/v1/portal/auth/login`                                           |
| Session     | `GET /api/v1/portal/auth/me` + refresh                                     |
| Cases       | `GET /api/v1/portal/cases`                                                 |
| Readiness   | `GET /api/v1/portal/cases/{id}/readiness`                                  |
| AI insights | `GET /api/v1/portal/cases/{id}/insights`                                   |
| Checklist   | `GET /api/v1/portal/cases/{id}/checklist` + `PATCH /portal/checklist/{id}` |
| Learning    | `GET /api/v1/portal/learning/modules` (+ complete/reopen)                  |
| Documents   | `/portal/cases/{id}/documents`                                             |
| Messages    | `/portal/cases/{id}/messages`                                              |
| Database    | Same Postgres as `apps/api`                                                |

Requires API flag: `ENABLE_CLIENT_PORTAL=true`.

Staff provisions borrowers via **Client → Portal user** (no self-serve signup).

## Local setup

1. Run the platform API (`apps/api`) with Postgres and `ENABLE_CLIENT_PORTAL=true`.
2. Ensure CORS includes `http://localhost:3100` (default in API config now includes it).
3. Copy env:

```bash
cp apps/lrp-web/.env.example apps/lrp-web/.env.local
```

4. Start portal:

```bash
pnpm --filter @verdin/api-client build
pnpm --filter @verdin/lrp-web dev
```

Open http://localhost:3100/portal/login

## Borrower portal routes

`/portal/dashboard` · `/timeline` · `/readiness` · `/tasks` · `/documents` · `/messages` · `/disputes` · `/ai-analysis` · `/progress` · `/learning` · `/notifications` · `/profile` · `/settings`

Readiness composite, AI insights, learning modules, and the task checklist are live on the portal realm (shared DB). Scores and insights remain advisory—not underwriting decisions or funding guarantees.

## Lender workspace

Demo partner workspace at `/lender/login` with local session auth (`lrp_lender_session` cookie + `localStorage`). Data is seeded in `src/lib/lender/data.ts` until Mortgage Partner APIs ship.

### Demo credentials

| Email              | Role               | Password      |
| ------------------ | ------------------ | ------------- |
| `admin@lrp.lender` | Lender admin       | `changeme123` |
| `lo@lrp.lender`    | Loan officer       | `changeme123` |
| `ops@lrp.lender`   | Credit operations  | `changeme123` |
| `uw@lrp.lender`    | Underwriter (view) | `changeme123` |

Open http://localhost:3100/lender/login or use **Open lender workspace** on `/lenders`.

### Lender routes

`/lender/dashboard` · `/referrals` · `/borrowers` · `/borrowers/[id]` · `/readiness` · `/pipeline` · `/documents` · `/messages` · `/analytics` · `/reports` · `/exports` · `/notifications` · `/admin` · `/permissions`

Readiness scores and exports are advisory composites for partner handoff—not credit scores, underwriting decisions, or funding guarantees.

## Enterprise CRM

Operator CRM at `/crm/login` with demo session auth (`lrp_crm_session` cookie + `localStorage`). Seeded domain in `src/lib/crm/data.ts`; maps to shared platform modules (clients, tasks, documents, notifications) with partner/referral APIs planned for Mortgage Partner edition.

### Demo credentials

| Email              | Role            | Password      |
| ------------------ | --------------- | ------------- |
| `admin@lrp.crm`    | CRM admin       | `changeme123` |
| `partners@lrp.crm` | Partner manager | `changeme123` |
| `lo@lrp.crm`       | Loan officer    | `changeme123` |
| `realtor@lrp.crm`  | Realtor liaison | `changeme123` |
| `ops@lrp.crm`      | Ops coordinator | `changeme123` |
| `readonly@lrp.crm` | Read only       | `changeme123` |

Open http://localhost:3100/crm/login or **Open enterprise CRM** on `/partners`.

### CRM routes

`/crm/dashboard` · `/partners` · `/borrowers` · `/borrowers/[id]` · `/lenders` · `/realtors` · `/referrals` · `/tasks` · `/workflow` · `/pipeline` · `/automations` · `/calendar` · `/documents` · `/notes` · `/sms` · `/email` · `/reporting` · `/admin` · `/permissions`
