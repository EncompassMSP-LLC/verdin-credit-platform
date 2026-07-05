# Version 5.9 Scope & Deferrals

Formal scope for **Version 5.9 — Compliance-Gated Autonomous Production**. Builds on shipped **v5.8.0** production integration scaffolds.

**Kickoff date:** 2026-07-05  
**Target:** Ship the next layer of 5.8-deferred autonomous production depth — agent unsupervised loops, autonomous bureau filing audit, live Stripe Tax API scaffold, and SAML automated rotation — without arbitrary code execution, filing without compliance review, or live external API calls without operator gates.

## Theme

Extend partial 5.8 compliance-gated scaffolds (supervised loops, bureau live API, tax calculation, HRIS lifecycle) toward compliance-approved autonomous production execution. Each epic ships as a **Partial** capability behind feature flags with tests and documentation.

## Epic outcomes (planned)

| Epic | Theme                    | 5.9 outcome | Summary                                                           |
| ---- | ------------------------ | ----------- | ----------------------------------------------------------------- |
| 1    | Agent unsupervised loops | Partial     | Multi-step loop audit without per-step human gates between steps  |
| 2    | Autonomous bureau filing | Partial     | Operator-gated autonomous filing run audit from invoked API runs  |
| 3    | Live Stripe Tax API      | Partial     | Admin-gated live Stripe Tax calculation invocation audit scaffold |
| 4    | SAML automated rotation  | Partial     | Federation cert automated rotation run audit scaffold             |

## Shipped from 5.8 (foundation — do not regress)

All v5.8.0 APIs, feature flags, migrations, worker jobs, portal UI, and `@verdin/api-client` functions remain production capabilities. See [`version-5.8-scope.md`](version-5.8-scope.md) and [`version-5.8-completion-checklist.md`](../development/version-5.8-completion-checklist.md).

## Explicit deferrals (not 5.9)

| Capability                     | Deferred to | Reason                                            |
| ------------------------------ | ----------- | ------------------------------------------------- |
| Arbitrary agent code execution | 5.10+       | Requires unsupervised loop scaffold in production |
| Unsupervised bureau re-filing  | 5.10+       | Legal/compliance review beyond filing audit       |
| Native mobile apps             | 5.10+       | Web-first production                              |
| Public OAuth dev portal        | 5.10+       | After internal developer portal stabilizes        |
| Cross-org benchmarks           | 5.10+       | Multi-tenant analytics policy not approved        |
| HRIS passwordless enrollment   | 5.10+       | After SAML automated rotation scaffold stabilizes |
| Multi-IdP bulk provisioning    | 5.10+       | After HRIS lifecycle sync scaffold stabilizes     |
| Automated charge retries       | 5.10+       | After live Stripe Tax API scaffold stabilizes     |

## Partial capability limits (5.9 targets)

### Agent unsupervised loops (Partial)

**Included:** Unsupervised loop run audit table, org-scoped status/list endpoints, admin-gated start scaffold when linked supervised loop runs are `approved`.

**Not included:** Arbitrary code execution, PII export without scrub config, loops without compliance policy linkage.

### Autonomous bureau filing (Partial)

**Included:** Autonomous filing run audit, org-scoped status/list endpoints, admin-gated filing scaffold when linked bureau live API runs are `invoked`.

**Not included:** Unsupervised re-filing loops, filing without operator review, automated re-dispute scheduling.

### Live Stripe Tax API (Partial)

**Included:** Live tax API invocation run audit, org-scoped status/list endpoints, admin-gated invoke scaffold when linked tax calculation runs are `calculated`.

**Not included:** Live Stripe Tax API calls without compliance deferral docs, automated charge retries, dunning legal template generation.

### SAML automated rotation (Partial)

**Included:** Automated rotation run audit, org-scoped status/list endpoints, enqueue scaffold when SAML cert rotation runs are `rotated`.

**Not included:** Rotation without operator review, multi-IdP bulk cert rollout, passwordless enrollment UI.

## Related documents

- [Version 5.9 completion checklist](../development/version-5.9-completion-checklist.md)
- [Version 5.8 scope](version-5.8-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
