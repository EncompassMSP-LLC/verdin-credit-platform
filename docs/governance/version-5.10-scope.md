# Version 5.10 Scope & Deferrals

Formal scope for **Version 5.10 — Compliance-Gated Production Automation**. Builds on shipped **v5.9.0** autonomous production scaffolds.

**Kickoff date:** 2026-07-05  
**Target:** Ship the next layer of 5.9-deferred production automation depth — agent arbitrary execution audit, bureau re-filing audit, Stripe charge retry scaffold, and SAML passwordless enrollment — without unsupervised re-filing loops, live charge retries without compliance review, or passwordless rollout without operator gates.

## Theme

Extend partial 5.9 compliance-gated scaffolds (unsupervised loops, autonomous filing, live Tax API, SAML automated rotation) toward compliance-approved production automation execution. Each epic ships as a **Partial** capability behind feature flags with tests and documentation.

## Epic outcomes (shipped — Partial ✅)

| Epic | Theme                        | 5.10 outcome | Summary                                                        |
| ---- | ---------------------------- | ------------ | -------------------------------------------------------------- |
| 1    | Agent arbitrary execution    | Partial ✅   | Admin-gated arbitrary execution run audit from completed loops |
| 2    | Bureau re-filing audit       | Partial ✅   | Operator-gated re-filing run audit from approved filing runs   |
| 3    | Stripe charge retry          | Partial ✅   | Admin-gated charge retry run audit from approved live Tax runs |
| 4    | SAML passwordless enrollment | Partial ✅   | Federation passwordless enrollment run audit scaffold          |

## Shipped from 5.9 (foundation — do not regress)

All v5.9.0 APIs, feature flags, migrations, worker jobs, portal UI, and `@verdin/api-client` functions remain production capabilities. See [`version-5.9-scope.md`](version-5.9-scope.md) and [`version-5.9-completion-checklist.md`](../development/version-5.9-completion-checklist.md).

## Explicit deferrals (not 5.10)

| Capability                   | Deferred to | Reason                                              |
| ---------------------------- | ----------- | --------------------------------------------------- |
| Unsupervised re-filing loops | 5.11+       | Legal/compliance beyond re-filing audit scaffold    |
| Live charge retries          | 5.11+       | Requires charge retry scaffold + billing policy     |
| Native mobile apps           | 5.11+       | Web-first production                                |
| Public OAuth dev portal      | 5.11+       | After internal developer portal stabilizes          |
| Cross-org benchmarks         | 5.11+       | Multi-tenant analytics policy not approved          |
| HRIS passwordless UI         | 5.11+       | After SAML passwordless enrollment scaffold         |
| Multi-IdP bulk provisioning  | 5.11+       | After SAML passwordless enrollment stabilizes       |
| PII export without scrub     | 5.11+       | Requires arbitrary execution scaffold in production |

## Partial capability limits (5.10 targets)

### Agent arbitrary execution (Partial)

**Included:** Arbitrary execution run audit table, org-scoped status/list endpoints, admin-gated start scaffold when linked unsupervised loop runs are `approved`.

**Not included:** PII export without scrub config, execution without compliance policy linkage, fully autonomous agents without admin approval.

### Bureau re-filing audit (Partial)

**Included:** Re-filing run audit, org-scoped status/list endpoints, operator-gated re-filing scaffold when linked autonomous filing runs are `approved`.

**Not included:** Unsupervised re-filing loops, re-filing without operator review, automated re-dispute scheduling.

### Stripe charge retry (Partial)

**Included:** Charge retry run audit, org-scoped status/list endpoints, admin-gated retry scaffold when linked live Tax API runs are `approved`.

**Not included:** Live charge retries without compliance deferral docs, dunning legal template generation, automated collections without operator gates.

### SAML passwordless enrollment (Partial)

**Included:** Passwordless enrollment run audit, org-scoped status/list endpoints, enqueue scaffold when SAML automated rotation runs are `automated`.

**Not included:** Passwordless rollout without operator review, multi-IdP bulk cert rollout, native mobile passkey UI.

## Related documents

- [Version 5.10 completion checklist](../development/version-5.10-completion-checklist.md)
- [Version 5.9 scope](version-5.9-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
