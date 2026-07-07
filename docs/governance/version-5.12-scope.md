# Version 5.12 Scope & Deferrals

Formal scope for **Version 5.12 — Compliance-Gated Expansion Surfaces**. Builds on shipped **v5.11.0** production execution scaffolds.

**Kickoff date:** 2026-07-07  
**Target:** Ship the next layer of 5.11-deferred production depth — live bureau API invocation scaffold, public OAuth developer portal scaffold, cross-org benchmark read model scaffold, and mobile passkey readiness scaffold — without unsupervised external execution or unreviewed compliance-sensitive data export.

## Theme

Extend partial 5.11 compliance-gated scaffolds (unsupervised re-filing, live charge retry execution, HRIS passwordless UI, multi-IdP bulk provisioning) toward controlled external integration and developer access surfaces. Each epic ships as a **Partial** capability behind feature flags with tests and documentation.

## Epic outcomes (planned)

| Epic | Theme                         | 5.12 outcome | Summary                                                              |
| ---- | ----------------------------- | ------------ | -------------------------------------------------------------------- |
| 1    | Bureau live API invocation    | Partial ✅   | Operator-gated bureau API invocation audit from approved filing prep |
| 2    | Public OAuth developer portal | Partial ✅   | Org-scoped OAuth app registration audit scaffold                     |
| 3    | Cross-org benchmark analytics | Partial ✅   | Governance-gated cross-org benchmark read model scaffold             |
| 4    | Mobile passkey readiness      | Partial      | Passkey enrollment readiness and audit surface (no native app)       |

## Shipped from 5.11 (foundation — do not regress)

All v5.11.0 APIs, feature flags, migrations, worker jobs, UI scaffolds, and `@verdin/api-client` functions remain production capabilities. See [`version-5.11-scope.md`](version-5.11-scope.md) and [`version-5.11-completion-checklist.md`](../development/version-5.11-completion-checklist.md).

## Explicit deferrals (not 5.12)

| Capability                               | Deferred to | Reason                                                      |
| ---------------------------------------- | ----------- | ----------------------------------------------------------- |
| Fully autonomous bureau API filing       | 5.13+       | Requires stronger compliance controls and operator override |
| Third-party OAuth marketplace publishing | 5.13+       | Legal/compliance partner review not complete                |
| Native mobile apps                       | 5.13+       | Web-first passkey readiness before native distribution      |
| Unredacted cross-org analytics exports   | 5.13+       | Data governance policy and approval workflow not finalized  |

## Partial capability limits (5.12 targets)

### Bureau live API invocation (Partial)

**Included:** API invocation run audit, org-scoped status/list endpoints, operator-gated start scaffold from approved internal runs.

**Not included:** Unsupervised live bureau filing, automatic retries without operator review, direct external submission loops.

### Public OAuth developer portal (Partial)

**Included:** OAuth app registration and key lifecycle audit, org-scoped status/list endpoints, admin-gated app publish scaffold.

**Not included:** Public marketplace publishing, unreviewed third-party access approvals, automated trust scoring.

### Cross-org benchmark analytics (Partial)

**Included:** Aggregated benchmark read model scaffold, governance-gated API access, audit logs for benchmark query runs.

**Not included:** Raw tenant data export, PII-including benchmark payloads, unrestricted benchmark dimensions.

### Mobile passkey readiness (Partial)

**Included:** Passkey readiness and enrollment audit scaffolds exposed through web surfaces and API endpoints.

**Not included:** Native mobile app clients, device attestation rollout, passwordless enforcement without operator gates.

## Related documents

- [Version 5.12 completion checklist](../development/version-5.12-completion-checklist.md)
- [Version 5.11 scope](version-5.11-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
