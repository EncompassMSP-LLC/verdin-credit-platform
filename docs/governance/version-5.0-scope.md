# Version 5.0 Scope & Deferrals

Formal scope for **Version 5.0 — Enterprise Edition**. Builds on the shipped **v4.8.0** Operations release.

**Kickoff date:** 2026-07-02  
**Target tag:** `v5.0.0`

## Theme

Enterprise-grade credit repair operations: compliance, identity, production communications, post-gate LLM assistance, job orchestration parity, and expanded client portal — without regressing Automation (4.5) or Operations (4.8) foundations.

## Epic outcomes (planned)

| Epic | Theme                 | v5.0.0 target | Summary                                                    |
| ---- | --------------------- | ------------- | ---------------------------------------------------------- |
| 1    | Data & client linking | Partial       | `cases.client_id` FK; durable case ↔ client relationship   |
| 2    | Communications        | Partial       | Production email delivery; SMS scaffold                    |
| 3    | AI Assistance (LLM)   | Partial       | Case summary endpoint(s) behind `ENABLE_LLM` + ADR-012     |
| 4    | Platform operations   | Partial       | Job orchestrator runner wiring; scheduled job registration |
| 5    | Enterprise identity   | Partial       | SSO and/or MFA foundation (feature-flagged)                |
| 6    | Compliance            | Partial       | Compliance center scaffold; consent/retention models       |
| 7    | Client portal         | Partial       | Document upload; secure messaging foundation               |
| 8    | Enterprise admin      | Partial       | Org admin expansions; API keys scaffold                    |
| 9    | Reporting & analytics | Partial       | Bureau performance and team productivity read models       |

## Shipped from 4.8 (foundation — do not regress)

In-app notifications, email delivery readiness gate, client/contact CRUD, portal auth + read-only case progress, LLM policy gates (`packages/llm-gateway/`), operations reporting read model, overdue investigation worker, and `job-orchestrator` package scaffold remain production capabilities.

## Explicit deferrals (still not 5.0)

| Capability                    | Deferred to | Reason                                   |
| ----------------------------- | ----------- | ---------------------------------------- |
| Autonomous dispute filing     | 5.0+        | Compliance and legal review gates        |
| Full BPM workflow designer    | 5.0+        | Scope beyond enterprise RC               |
| Multi-tenant billing / Stripe | 5.1+        | Requires product + finance sign-off      |
| Predictive outcome models     | 5.1+        | Needs historical data pipeline           |
| AI Phase 4 autonomous agents  | 5.1+        | Compliance + observability prerequisites |
| Native mobile apps            | 5.1+        | Web-first enterprise RC                  |

## Partial capability limits (5.0 targets)

### Data & client linking (Partial)

**Included:** Alembic migration for optional `cases.client_id`; staff API updates; portal case matching prefers FK when set.

**Not included:** Full client intake wizard, bulk import, CRM sync.

### Communications (Partial)

**Included:** Production email send via configured provider (`smtp` / `sendgrid`); delivery audit trail; notification workflow integration.

**Not included:** SMS production delivery (scaffold only), marketing campaigns, deliverability dashboards.

### AI Assistance — LLM (Partial)

**Included:** At least one staff-authenticated summary endpoint (case-level) calling external provider only when `require_llm_ready()` passes.

**Not included:** Document summaries, autonomous agents, external PII export without org opt-in.

### Platform operations (Partial)

**Included:** Wire runner retries/metrics; register overdue scan on scheduler scaffold.

**Not included:** PostgreSQL job persistence, cron admin UI, cross-org SLA dashboards.

### Enterprise identity (Partial)

**Included:** MFA and/or SSO integration scaffold behind `ENABLE_ENTERPRISE`; staff auth partition unchanged for portal.

**Not included:** Full IdP catalog, SCIM provisioning, per-org SAML metadata UI.

### Compliance (Partial)

**Included:** Compliance center module scaffold; consent record model; retention policy placeholders.

**Not included:** Legal sign-off workflows, automated filing with bureaus, full audit export suite.

### Client portal (Partial)

**Included:** Client document upload (scoped to linked cases); messaging thread scaffold.

**Not included:** Billing, credit score history charts, mobile push.

### Enterprise admin (Partial)

**Included:** Organization summary metrics, API key create/list/revoke with hashed storage, org-admin status endpoint behind `ENABLE_ENTERPRISE`.

**Not included:** SCIM provisioning, billing administration, cross-org admin roles, API key usage analytics, key-authenticated API middleware.

### Reporting & analytics (Partial)

**Included:** Bureau performance and team productivity org-scoped read models; enterprise reporting status endpoint.

**Not included:** Materialized views, revenue metrics, score-improvement trends, scheduled report delivery.

## v5.0.0 sign-off

All nine epics ship as **Partial** with written limits above. No **Planned** 5.0 roadmap items remain undocumented — autonomous agents, full BPM, billing, predictive analytics, and native mobile apps are deferred to **5.0+** or **5.1+** per the deferrals table.

| Epic                  | v5.0.0 status | Notes                                                               |
| --------------------- | ------------- | ------------------------------------------------------------------- |
| Data & client linking | Partial ✅    | `cases.client_id` FK; portal FK + heuristic match                   |
| Communications        | Partial ✅    | Production email + audit log; SMS production deferred               |
| AI Assistance (LLM)   | Partial ✅    | Case summary endpoint post-gate; document summaries deferred        |
| Platform operations   | Partial ✅    | Job orchestrator retry/metrics + overdue cron registration          |
| Enterprise identity   | Partial ✅    | SSO/MFA readiness scaffold; IdP/TOTP enrollment deferred            |
| Compliance            | Partial ✅    | Consent records + retention placeholders; enforcement deferred      |
| Client portal         | Partial ✅    | Document upload + messaging scaffold; real-time delivery deferred   |
| Enterprise admin      | Partial ✅    | Org summary + API key lifecycle; SCIM/billing deferred              |
| Reporting & analytics | Partial ✅    | Bureau performance + team productivity; materialized views deferred |

## Related documents

- [Version 5.0 completion checklist](../development/version-5.0-completion-checklist.md)
- [V5.0 Enterprise Roadmap](../roadmap/v5.0-enterprise.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [Version 4.8 scope](version-4.8-scope.md)
