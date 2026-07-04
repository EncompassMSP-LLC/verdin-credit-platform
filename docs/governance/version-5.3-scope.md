# Version 5.3 Scope & Deferrals

Formal scope for **Version 5.3 — Enterprise Depth**. Builds on shipped **v5.2.0** deferred production surfaces.

**Kickoff date:** 2026-07-04  
**Target:** Ship scaffolds for 5.2-deferred enterprise integrations — usage metering, SCIM, predictive analytics, and API developer surfaces — without autonomous filing or native mobile apps.

## Theme

Extend partial 5.1–5.2 enterprise foundations (Stripe billing, IdP enrollment, API keys, revenue read models) toward operator-ready production depth. Each epic ships as a **Partial** capability behind feature flags with tests and documentation.

## Epic outcomes (planned)

| Epic | Theme                  | 5.3 target | Summary                                                       |
| ---- | ---------------------- | ---------- | ------------------------------------------------------------- |
| 1    | Billing usage metering | Partial    | Org-scoped usage event scaffold + reporting read model        |
| 2    | Identity provisioning  | Partial    | SCIM 2.0 user/group provision scaffold behind enterprise gate |
| 3    | Predictive analytics   | Partial    | Historical outcome read model + staff reporting endpoint      |
| 4    | API integrations depth | Partial    | API key rotation + internal developer portal scaffold         |
| 5    | LLM operations depth   | Partial    | Batch document summarization job scaffold (ADR-012 gates)     |

## Shipped from 5.2 (foundation — do not regress)

All v5.2.0 APIs, feature flags, migrations, worker jobs, portal UI, and `@verdin/api-client` functions remain production capabilities. See [`version-5.2-scope.md`](version-5.2-scope.md) and [`version-5.2-completion-checklist.md`](../development/version-5.2-completion-checklist.md).

## Explicit deferrals (not 5.3)

| Capability                | Deferred to | Reason                                          |
| ------------------------- | ----------- | ----------------------------------------------- |
| Autonomous dispute filing | 5.4+        | Legal/compliance review beyond 5.3              |
| AI autonomous agents      | 5.4+        | Observability + human-in-the-loop prerequisites |
| Native mobile apps        | 5.4+        | Web-first production                            |
| Invoicing PDFs / dunning  | 5.4+        | After usage metering validates in production    |
| Multi-IdP federation      | 5.4+        | After SCIM scaffold stabilizes                  |
| Marketing SMS campaigns   | 5.4+        | Deliverability ops not in 5.3                   |

## Partial capability limits (5.3 targets)

### Billing usage metering (Partial)

**Included:** Usage event recording scaffold, org-scoped metering read endpoint, linkage to existing Stripe billing account when `ENABLE_BILLING=true`.

**Not included:** Invoice PDF generation, dunning automation, cross-org usage benchmarks.

### Identity provisioning (Partial)

**Included:** SCIM 2.0 Users/Groups provision endpoints scaffold, audit events, enterprise gate alignment with existing OIDC enrollment.

**Not included:** Multi-IdP federation UI, passwordless, HRIS bidirectional sync.

### Predictive analytics (Partial)

**Included:** Org-scoped historical outcome aggregates read model, staff reporting endpoint, refresh scaffold behind `ENABLE_MATERIALIZED_REPORTING` or dedicated flag.

**Not included:** Cross-org benchmarks, real-time model serving, autonomous case prioritization.

### API integrations depth (Partial)

**Included:** API key rotation workflow, internal developer portal page listing keys/scopes/rate-limit status.

**Not included:** Public external developer portal, per-route limit configuration UI, OAuth client credentials for third parties.

### LLM operations depth (Partial)

**Included:** Worker job scaffold for batch document summarization with PII scrubbing and timeline audit.

**Not included:** LLM dispute draft augmentation, autonomous agents, external batch export.

## Related documents

- [Version 5.3 completion checklist](../development/version-5.3-completion-checklist.md)
- [Version 5.2 scope](version-5.2-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
