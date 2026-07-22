# Volume 24 — Technology architecture

| Field        | Value                    |
| ------------ | ------------------------ |
| Status       | `ready-for-build`        |
| Stage        | 4                        |
| Owner        | Engineering              |
| Last updated | 2026-07-22               |
| Depends on   | Vol 18 · Vol 22 · Vol 23 |

---

## 1. Default stack (edition on shared platform)

| Area                   | Choice                                                                        |
| ---------------------- | ----------------------------------------------------------------------------- |
| Frontend (LRP)         | Next.js, TypeScript, Tailwind — `apps/lrp-web`                                |
| Staff admin (platform) | React/Vite — `apps/web` (as needed)                                           |
| Backend                | FastAPI, SQLAlchemy, Alembic — `apps/api`                                     |
| Data                   | PostgreSQL (multi-tenant `organization_id`), Redis, object storage            |
| Workers                | `apps/worker`                                                                 |
| Auth                   | Platform JWT; portal realm; mortgage partner APIs (`ENABLE_MORTGAGE_PARTNER`) |
| AI                     | Deterministic analysis + optional LLM behind ADR-012 (Vol 22)                 |
| CI/CD                  | GitHub Actions                                                                |
| Observability          | structlog; metrics/tracing expand below                                       |

## 2. Decision: Supabase greenfield?

**Default for LRP: No.** Parallel Supabase recreates clients/cases/compliance and doubles maintenance.

To override: ADR in `docs/adr/` + this volume updated to `approved` with dual-maintenance analysis.

---

## 3. Environment topology

| Env        | Purpose                   | Data                    |
| ---------- | ------------------------- | ----------------------- |
| Local      | Dev docker compose / pnpm | Synthetic               |
| CI         | pytest + web checks       | `verdin_credit_test`    |
| Staging    | Partner demos / QA        | Anonymized or synthetic |
| Production | Live tenants              | Real PII — hardened     |

Diagram (logical):

```text
[lrp-web] → [API] → [Postgres]
                ↘ [Redis] → [Worker] → [Object storage]
                ↘ [Email/SMS providers]
```

## 4. Secrets management

- No secrets in git
- Env / secret manager per deploy target
- Separate Stripe/LLM/bureau credentials by env
- Rotate on role change (Vol 15 offboarding)

## 5. Backup & restore

| Item           | Draft target                                            |
| -------------- | ------------------------------------------------------- |
| Postgres       | Daily automated backups; weekly restore test in staging |
| Object storage | Versioning / replication per provider                   |
| RPO            | ≤ 24h (tighten with founder)                            |
| RTO            | ≤ 24h for core API (tighten with founder)               |

## 6. Disaster recovery

- Document failover region strategy (cloud TBD)
- Incident commander = founder/eng on-call draft
- Comms templates: status page or email

## 7. Scalability & tenancy

- All business rows scoped by `organization_id`
- Partner data scoped by partnership membership
- No cross-tenant analytics (Vol 18 / reporting rules)
- Horizontal API/worker scale behind load balancer when needed

## 8. Security / SOC2-ready mapping (draft)

| Control theme     | Approach                                         |
| ----------------- | ------------------------------------------------ |
| Access control    | RBAC + least privilege                           |
| Audit logging     | Mutations on score, dispute, export, partnership |
| Encryption        | TLS in transit; at-rest per cloud defaults       |
| SDLC              | PR reviews, CI, conventional commits             |
| Vendor management | DPAs for subprocessors (Vol 17)                  |

## 9. PII & LLM policy

- Align ADR-012 / `require_llm_ready()`
- Redact before external LLM unless org opt-in
- Partner digests minimize PII
- Export packages audited

## 10. Partner API versioning

- Mortgage partner module under feature flag
- Additive OpenAPI changes preferred
- Breaking changes require version path + changelog

## 11. Logging & monitoring

| Signal            | Tooling (draft)            |
| ----------------- | -------------------------- |
| App logs          | structlog → aggregator TBD |
| Uptime            | Health checks `/health`    |
| Error tracking    | TBD (Sentry or equiv.)     |
| Product analytics | Events from Vol 19–21      |

## 12. Stage 5 build constraints

- Implement only from volumes ≥ `ready-for-build`
- Prefer extending `apps/api` modules over new services
- LRP UI in `apps/lrp-web`; share `@verdin/api-client` types

## 13. Checklist

- [x] Default stack documented
- [x] Supabase decision defaulted (edition)
- [ ] Cloud provider + region locked
- [ ] RPO/RTO numbers signed by founder
- [ ] Error tracking vendor chosen
- [ ] Staging data policy signed

## Approval

| Role        | Name | Date | Sign-off |
| ----------- | ---- | ---- | -------- |
| Engineering |      |      | ☐        |
| Founder     |      |      | ☐        |
| Compliance  |      |      | ☐        |
