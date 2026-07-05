# Version 5.8 Scope & Deferrals

Formal scope for **Version 5.8 — Compliance-Gated Production Integrations**. Builds on shipped **v5.7.0** autonomous workflow scaffolds.

**Kickoff date:** 2026-07-05  
**Target:** Ship the next layer of 5.7-deferred production integration depth — agent supervised loops, bureau live API integration audit, Stripe tax calculation, and HRIS lifecycle sync — without fully unsupervised agent loops or autonomous bureau filing without human approval.

## Theme

Extend partial 5.7 compliance-gated scaffolds (bureau submission, tool-calling, cert rotation, invoice PDF) toward operator-supervised production integration execution. Each epic ships as a **Partial** capability behind feature flags with tests and documentation.

## Epic outcomes (planned)

| Epic | Theme                       | 5.8 outcome | Summary                                                      |
| ---- | --------------------------- | ----------- | ------------------------------------------------------------ |
| 1    | Agent supervised loops      | Partial     | Multi-step agent loop audit with human gates between steps   |
| 2    | Bureau live API integration | Partial     | Operator-gated external bureau API invocation audit scaffold |
| 3    | Stripe tax calculation      | Partial     | Org-scoped tax calculation run audit scaffold                |
| 4    | HRIS lifecycle sync         | Partial     | Full employee lifecycle sync run audit scaffold              |

## Shipped from 5.7 (foundation — do not regress)

All v5.7.0 APIs, feature flags, migrations, worker jobs, portal UI, and `@verdin/api-client` functions remain production capabilities. See [`version-5.7-scope.md`](version-5.7-scope.md) and [`version-5.7-completion-checklist.md`](../development/version-5.7-completion-checklist.md).

## Explicit deferrals (not 5.8)

| Capability                     | Deferred to | Reason                                           |
| ------------------------------ | ----------- | ------------------------------------------------ |
| Fully unsupervised agent loops | 5.9+        | Requires supervised loop scaffold in production  |
| Autonomous bureau filing       | 5.9+        | Legal/compliance review beyond live API scaffold |
| Native mobile apps             | 5.9+        | Web-first production                             |
| Public OAuth dev portal        | 5.9+        | After internal developer portal stabilizes       |
| Cross-org benchmarks           | 5.9+        | Multi-tenant analytics policy not approved       |
| SAML automated rotation        | 5.9+        | After cert rotation scaffold stabilizes          |
| Live Stripe PDF API calls      | 5.9+        | After tax calculation scaffold stabilizes        |

## Partial capability limits (5.8 targets)

### Agent supervised loops (Partial)

**Included:** Supervised loop run audit table, org-scoped status/list endpoints, admin-gated step progression scaffold when linked tool-calling runs are `invoked`.

**Not included:** Fully unsupervised loops, arbitrary code execution, PII export without scrub config.

### Bureau live API integration (Partial)

**Included:** Bureau API invocation run audit, org-scoped status/list endpoints, admin-gated invoke scaffold when linked submission run is `submitted`.

**Not included:** Unsupervised filing loops, automated re-dispute scheduling, filing without operator review.

### Stripe tax calculation (Partial)

**Included:** Tax calculation run audit, org-scoped status/list endpoints, enqueue scaffold when `ENABLE_BILLING=true` and invoice PDF runs exist.

**Not included:** Live Stripe Tax API calls without compliance deferral docs, automated charge retries, dunning legal template generation.

### HRIS lifecycle sync (Partial)

**Included:** Lifecycle sync run audit, org-scoped status/list endpoints, enqueue scaffold when HRIS bidirectional sync is ready.

**Not included:** Passwordless enrollment UI, multi-IdP bulk provisioning, automated cert rotation without operator review.

## Related documents

- [Version 5.8 completion checklist](../development/version-5.8-completion-checklist.md)
- [Version 5.7 scope](version-5.7-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
