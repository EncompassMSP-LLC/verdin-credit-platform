# Version 5.2 Scope & Deferrals

Formal scope for **Version 5.2 — Deferred Production Surfaces**. Builds on shipped **v5.1.0** production hardening.

**Kickoff date:** 2026-07-03  
**Target:** Complete 5.1-deferred communications and AI surfaces, plus incremental production depth for portal push and revenue reporting

## Theme

Finish the production integrations explicitly deferred from v5.1.0 — SMS delivery and LLM document summaries — and extend partial 5.1 scaffolds (Web Push, billing data) toward operator-ready production behavior without autonomous filing or mobile apps.

## Epic outcomes (planned)

| Epic | Theme                     | 5.2 target | Summary                                              |
| ---- | ------------------------- | ---------- | ---------------------------------------------------- |
| 1    | Communications production | Partial    | Production SMS delivery via Twilio alongside email   |
| 2    | LLM expansion             | Partial    | Document summary endpoint + staff UI (ADR-012 gates) |
| 3    | Portal push production    | Partial    | Real Web Push HTTP delivery for portal messaging     |
| 4    | Revenue analytics         | Partial    | Org-scoped revenue/readiness scaffold from billing   |
| 5    | API integrations depth    | Partial    | API key rate-limit scaffold on authenticated routes  |

## Shipped from 5.1 (foundation — do not regress)

All v5.1.0 APIs, feature flags, migrations, worker jobs, portal UI, and `@verdin/api-client` functions remain production capabilities. See [`version-5.1-scope.md`](version-5.1-scope.md) and [`version-5.1-completion-checklist.md`](../development/version-5.1-completion-checklist.md).

## Explicit deferrals (not 5.2)

| Capability                | Deferred to | Reason                                   |
| ------------------------- | ----------- | ---------------------------------------- |
| Autonomous dispute filing | 5.3+        | Legal/compliance review beyond 5.2       |
| SCIM provisioning         | 5.3+        | After IdP enrollment stabilizes in prod  |
| Predictive outcome models | 5.3+        | Historical data pipeline not ready       |
| AI autonomous agents      | 5.3+        | Observability + compliance prerequisites |
| Native mobile apps        | 5.3+        | Web-first production                     |
| Billing usage metering    | 5.3+        | After revenue scaffold validates         |
| Invoicing PDFs / dunning  | 5.3+        | Finance workflow not in 5.2              |

## Partial capability limits (5.2 targets)

### Communications production (Partial)

**Included:** Twilio SMS adapter, delivery audit log, notification workflow integration behind `ENABLE_SMS_DELIVERY`.

**Not included:** Marketing campaigns, deliverability dashboards, multi-provider failover UI.

### LLM expansion (Partial)

**Included:** `POST /documents/{id}/llm-summary` with PII scrubbing and timeline audit; staff document detail UI panel behind `ENABLE_LLM`.

**Not included:** LLM dispute draft augmentation, autonomous agents, batch summarization jobs.

### Portal push production (Partial)

**Included:** Web Push HTTP send for staff-message dispatch when VAPID + provider configured.

**Not included:** Mobile native push, cross-browser subscription management UI beyond 5.1 scaffold.

### Revenue analytics (Partial)

**Included:** Org-scoped revenue/readiness read model from Stripe billing account state; staff reporting endpoint.

**Not included:** Usage-based metering, invoicing, cross-org benchmarks.

### API integrations depth (Partial)

**Included:** Per-organization API key rate-limit scaffold on `GET /reporting/operations`.

**Not included:** Public developer portal, automated key rotation, per-route limit UI.

## Related documents

- [Version 5.2 completion checklist](../development/version-5.2-completion-checklist.md)
- [Version 5.1 scope](version-5.1-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
