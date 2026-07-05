# Version 5.6 Scope & Deferrals

Formal scope for **Version 5.6 — Compliance-Reviewed Production Depth**. Builds on shipped **v5.5.0** production automation scaffolds.

**Kickoff date:** 2026-07-04  
**Target:** Ship the next layer of 5.5-deferred production depth — HRIS sync, SMS deliverability dashboards, LLM dispute draft augment, and compliance-gated dispute filing prep — without autonomous bureau filing or unsupervised agent loops.

## Theme

Extend partial 5.5 production automation (invoice collection, SAML metadata, marketing SMS delivery, human-gated agent execution) toward compliance-reviewed operator workflows. Each epic ships as a **Partial** capability behind feature flags with tests and documentation.

## Epic outcomes (planned)

| Epic | Theme                         | 5.6 outcome | Summary                                                              |
| ---- | ----------------------------- | ----------- | -------------------------------------------------------------------- |
| 1    | HRIS bidirectional sync       | Partial ✅  | Org-scoped HRIS sync run audit + status scaffold                     |
| 2    | SMS deliverability dashboards | Partial ✅  | Marketing SMS delivery metrics read model + staff status endpoint    |
| 3    | LLM dispute draft augment     | Partial ✅  | ADR-012-gated dispute letter augment scaffold (no auto-send)         |
| 4    | Dispute filing prep           | Partial ✅  | Compliance-gated filing prep audit (no autonomous bureau submission) |

## Shipped from 5.5 (foundation — do not regress)

All v5.5.0 APIs, feature flags, migrations, worker jobs, portal UI, and `@verdin/api-client` functions remain production capabilities. See [`version-5.5-scope.md`](version-5.5-scope.md) and [`version-5.5-completion-checklist.md`](../development/version-5.5-completion-checklist.md).

## Explicit deferrals (not 5.6)

| Capability                 | Deferred to | Reason                                         |
| -------------------------- | ----------- | ---------------------------------------------- |
| Autonomous dispute filing  | 5.7+        | Legal/compliance review beyond filing prep     |
| AI fully autonomous agents | 5.7+        | Requires dispute prep + human approval in prod |
| Native mobile apps         | 5.7+        | Web-first production                           |
| Public OAuth dev portal    | 5.7+        | After internal developer portal stabilizes     |
| Cross-org benchmarks       | 5.7+        | Multi-tenant analytics policy not approved     |
| Stripe invoice PDF + tax   | 5.7+        | After collection scaffold stabilizes           |
| SAML cert auto-rotation    | 5.7+        | After HRIS sync scaffold stabilizes            |

## Partial capability limits (5.6 targets)

### HRIS bidirectional sync (Partial)

**Included:** HRIS sync run audit table, org-scoped sync status endpoint, enqueue scaffold when `ENABLE_ENTERPRISE=true`.

**Not included:** Full employee lifecycle sync, passwordless enrollment UI, automated certificate rotation.

### SMS deliverability dashboards (Partial)

**Included:** Delivery metrics aggregate read model, org-scoped deliverability status endpoint, campaign run outcome summary.

**Not included:** Multi-provider failover, A/B testing, opt-out compliance automation, real-time alerting.

### LLM dispute draft augment (Partial)

**Included:** ADR-012-gated augment request audit, dispute letter augment scaffold endpoint, staff review correlation on case timeline.

**Not included:** Autonomous letter send, unsupervised LLM loops, PII export without scrub config.

### Dispute filing prep (Partial)

**Included:** Compliance-gated filing prep run audit, status/list endpoints, admin approval before any external submission scaffold.

**Not included:** Autonomous bureau filing, external tool calling without approval, unsupervised agent loops.

## Related documents

- [Version 5.6 completion checklist](../development/version-5.6-completion-checklist.md)
- [Version 5.5 scope](version-5.5-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
