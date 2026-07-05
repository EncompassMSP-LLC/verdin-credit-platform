# Version 5.7 Scope & Deferrals

Formal scope for **Version 5.7 — Compliance-Gated Autonomous Workflows**. Builds on shipped **v5.6.0** compliance-reviewed production depth scaffolds.

**Kickoff date:** 2026-07-05  
**Target:** Ship the next layer of 5.6-deferred autonomous workflow depth — bureau submission scaffold, agent tool-calling audit, SAML certificate rotation, and Stripe invoice PDF generation — without unsupervised agent loops or fully autonomous bureau filing.

## Theme

Extend partial 5.6 compliance-reviewed scaffolds (filing prep, LLM augment, HRIS sync, deliverability) toward operator-gated autonomous workflow execution. Each epic ships as a **Partial** capability behind feature flags with tests and documentation.

## Epic outcomes (planned)

| Epic | Theme                       | 5.7 outcome | Summary                                                          |
| ---- | --------------------------- | ----------- | ---------------------------------------------------------------- |
| 1    | Dispute bureau submission   | Partial     | Admin-gated bureau submission run audit (no unsupervised filing) |
| 2    | Agent external tool-calling | Partial     | Human-gated external tool invocation audit scaffold              |
| 3    | SAML certificate rotation   | Partial     | Federation cert rotation run audit + status scaffold             |
| 4    | Stripe invoice PDF          | Partial     | Org-scoped invoice PDF generation run audit scaffold             |

## Shipped from 5.6 (foundation — do not regress)

All v5.6.0 APIs, feature flags, migrations, worker jobs, portal UI, and `@verdin/api-client` functions remain production capabilities. See [`version-5.6-scope.md`](version-5.6-scope.md) and [`version-5.6-completion-checklist.md`](../development/version-5.6-completion-checklist.md).

## Explicit deferrals (not 5.7)

| Capability                     | Deferred to | Reason                                               |
| ------------------------------ | ----------- | ---------------------------------------------------- |
| Fully unsupervised agent loops | 5.8+        | Requires tool-calling + submission scaffolds in prod |
| Autonomous bureau filing       | 5.8+        | Legal/compliance review beyond submission scaffold   |
| Native mobile apps             | 5.8+        | Web-first production                                 |
| Public OAuth dev portal        | 5.8+        | After internal developer portal stabilizes           |
| Cross-org benchmarks           | 5.8+        | Multi-tenant analytics policy not approved           |
| Full HRIS lifecycle sync       | 5.8+        | After HRIS sync scaffold stabilizes                  |
| Stripe tax calculation         | 5.8+        | After invoice PDF scaffold stabilizes                |

## Partial capability limits (5.7 targets)

### Dispute bureau submission (Partial)

**Included:** Bureau submission run audit table, org-scoped status/list endpoints, admin-gated submit scaffold when linked prep run is `prepared`.

**Not included:** Unsupervised filing loops, external bureau API integration without compliance deferral docs, automated re-dispute scheduling.

### Agent external tool-calling (Partial)

**Included:** Tool invocation request audit, status/list endpoints, admin approval before external tool execution scaffold.

**Not included:** Unsupervised tool loops, arbitrary code execution, PII export to external tools without scrub config.

### SAML certificate rotation (Partial)

**Included:** Certificate rotation run audit, org-scoped rotation status endpoint, enqueue scaffold when `ENABLE_ENTERPRISE=true`.

**Not included:** Automated rotation without operator review, multi-IdP bulk rotation UI, passwordless enrollment.

### Stripe invoice PDF (Partial)

**Included:** Invoice PDF generation run audit, org-scoped status/list endpoints, enqueue scaffold when `ENABLE_BILLING=true`.

**Not included:** Tax calculation, automated charge retries, dunning legal template generation.

## Related documents

- [Version 5.7 completion checklist](../development/version-5.7-completion-checklist.md)
- [Version 5.6 scope](version-5.6-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
