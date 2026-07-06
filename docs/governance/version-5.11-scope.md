# Version 5.11 Scope & Deferrals

Formal scope for **Version 5.11 — Compliance-Gated Production Execution**. Builds on shipped **v5.10.0** production automation scaffolds.

**Kickoff date:** 2026-07-06  
**Target:** Ship the next layer of 5.10-deferred production execution depth — unsupervised bureau re-filing audit, live Stripe charge retry execution scaffold, HRIS passwordless UI scaffold, and multi-IdP bulk provisioning — without native mobile apps, public OAuth dev portals, or cross-org benchmarks without policy approval.

## Theme

Extend partial 5.10 compliance-gated scaffolds (arbitrary execution, bureau re-filing, charge retry, SAML passwordless enrollment) toward compliance-approved production execution. Each epic ships as a **Partial** capability behind feature flags with tests and documentation.

## Epic outcomes (planned)

| Epic | Theme                         | 5.11 outcome | Summary                                                           |
| ---- | ----------------------------- | ------------ | ----------------------------------------------------------------- |
| 1    | Unsupervised bureau re-filing | Partial      | Operator-gated unsupervised re-filing run audit from refiled runs |
| 2    | Live charge retry execution   | Partial      | Admin-gated live charge retry execution audit from retried runs   |
| 3    | HRIS passwordless UI          | Partial      | HRIS-linked passwordless enrollment UI audit scaffold             |
| 4    | Multi-IdP bulk provisioning   | Partial      | Federation bulk IdP provisioning run audit scaffold               |

## Shipped from 5.10 (foundation — do not regress)

All v5.10.0 APIs, feature flags, migrations, worker jobs, portal UI, and `@verdin/api-client` functions remain production capabilities. See [`version-5.10-scope.md`](version-5.10-scope.md) and [`version-5.10-completion-checklist.md`](../development/version-5.10-completion-checklist.md).

## Explicit deferrals (not 5.11)

| Capability               | Deferred to | Reason                                              |
| ------------------------ | ----------- | --------------------------------------------------- |
| Native mobile apps       | 5.12+       | Web-first production                                |
| Public OAuth dev portal  | 5.12+       | After internal developer portal stabilizes          |
| Cross-org benchmarks     | 5.12+       | Multi-tenant analytics policy not approved          |
| PII export without scrub | 5.12+       | Requires compliance policy ADR beyond 5.10 scaffold |
| Live bureau API calls    | 5.12+       | After unsupervised re-filing scaffold stabilizes    |
| Dunning legal templates  | 5.12+       | Legal review beyond charge retry execution scaffold |

## Partial capability limits (5.11 targets)

### Unsupervised bureau re-filing (Partial)

**Included:** Unsupervised re-filing run audit, org-scoped status/list endpoints, operator-gated start scaffold when linked bureau re-filing runs are `refiled`.

**Not included:** Re-filing without operator review, automated re-dispute scheduling, live bureau API calls without compliance deferral docs.

### Live charge retry execution (Partial)

**Included:** Live charge retry execution run audit, org-scoped status/list endpoints, admin-gated execution scaffold when linked charge retry runs are `retried`.

**Not included:** Live Stripe charge API calls without compliance deferral docs, automated collections without operator gates, dunning legal template generation.

### HRIS passwordless UI (Partial)

**Included:** HRIS passwordless UI enrollment run audit, org-scoped status/list endpoints, admin-gated UI scaffold when linked SAML passwordless enrollment runs are `enrolled`.

**Not included:** Native mobile passkey UI, passwordless rollout without operator review, multi-IdP bulk cert rollout.

### Multi-IdP bulk provisioning (Partial)

**Included:** Bulk IdP provisioning run audit, org-scoped status/list endpoints, admin-gated provisioning scaffold when linked HRIS passwordless UI runs are `approved`.

**Not included:** Provisioning without operator review, cross-org IdP templates, automated cert rotation without admin gates.

## Related documents

- [Version 5.11 completion checklist](../development/version-5.11-completion-checklist.md)
- [Version 5.10 scope](version-5.10-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
