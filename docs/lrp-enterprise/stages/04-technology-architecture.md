# Stage 4 — Technology Architecture

**Goal:** Decide (and document) how LRP is built, secured, and operated — before Stage 5 coding.

## Default posture (monorepo edition)

| Layer    | Default choice                            | Notes                                      |
| -------- | ----------------------------------------- | ------------------------------------------ |
| Frontend | Next.js · TypeScript · Tailwind           | Already in `apps/lrp-web`                  |
| Backend  | FastAPI · PostgreSQL · Redis · workers    | Shared `apps/api` — multi-tenant           |
| Auth     | Platform JWT + portal / partner realms    | Partner JWT still maturing                 |
| AI       | Deterministic engines + ADR-012 LLM gates | Credit analysis module exists as reference |
| Infra    | Docker · CI (GitHub Actions) · cloud TBD  | Document DR, backups, monitoring in Vol 24 |

## Explicit decision required

A common greenfield proposal is **Supabase + RLS + Edge Functions + Vercel**.

For LRP **as an edition of Ultimate Credit Repair**, the default is **reuse the shared platform**, not stand up a parallel Supabase app that duplicates cases/clients/compliance.

If greenfield Supabase is preferred, Stage 4 must produce an **ADR** that supersedes “edition on shared platform,” with cost, compliance, and dual-maintenance analysis.

## Also document in Vol 24

- Security & SOC2-ready controls
- Backups & disaster recovery
- Scalability & tenancy
- Logging, monitoring, incident response
- Secrets management
- Environments (dev / staging / prod)

## Progress

- [x] Default stack + anti-Supabase default documented (Vol 24)
- [x] Topology, secrets, DR, tenancy, security, LLM, API versioning drafted
- [ ] Cloud region / RPO-RTO / error tracking signed

## Exit gate

Vol 24 at `approved` + any stack ADRs merged.
