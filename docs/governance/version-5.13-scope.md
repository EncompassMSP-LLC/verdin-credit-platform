# Version 5.13 Scope & Deferrals

Formal scope for **Version 5.13 — Native Mobile Depth**. Builds on shipped **v5.12.0** compliance-gated expansion scaffolds.

**Kickoff date:** 2026-07-07  
**Sign-off date:** 2026-07-10  
**Target:** Ship the next layer of 5.12-deferred production depth — native mobile passkey client scaffold, OAuth marketplace publishing scaffold, fully autonomous bureau API filing scaffold, and unredacted cross-org benchmark export scaffold — without unsupervised live external execution, public marketplace distribution, or live unredacted data export.

## Theme

Extend partial 5.12 expansion surfaces (bureau live API, public OAuth portal, cross-org benchmarks, mobile passkey readiness) toward operator-gated native client, marketplace, autonomous filing, and export audit scaffolds. Each epic ships as a **Partial** capability behind feature flags with tests and documentation.

## Epic outcomes (shipped)

| Epic | Theme                                 | 5.13 outcome | Summary                                                                   |
| ---- | ------------------------------------- | ------------ | ------------------------------------------------------------------------- |
| 1    | Native mobile passkey client          | Partial ✅   | Operator-gated native passkey client enrollment audit from readiness runs |
| 2    | OAuth marketplace publishing          | Partial ✅   | Admin-gated marketplace listing audit from approved OAuth apps            |
| 3    | Fully autonomous bureau API filing    | Partial ✅   | Admin-gated fully autonomous API filing audit from filed autonomous runs  |
| 4    | Unredacted cross-org benchmark export | Partial ✅   | Admin-gated export audit from completed cross-org benchmark refresh runs  |

## Shipped from 5.12 (foundation — do not regress)

All v5.12.0 APIs, feature flags, migrations, UI scaffolds, and `@verdin/api-client` functions remain production capabilities. See [`version-5.12-scope.md`](version-5.12-scope.md) and [`version-5.12-completion-checklist.md`](../development/version-5.12-completion-checklist.md).

## Explicit deferrals (not 5.13)

| Capability                            | Deferred to | Reason                                                      |
| ------------------------------------- | ----------- | ----------------------------------------------------------- |
| Live unredacted benchmark blob export | 5.14+       | Data governance and secure export pipeline not built        |
| Unsupervised autonomous filing loops  | 5.14+       | Stronger compliance controls and operator override required |
| Public OAuth marketplace listings     | 5.14+       | Legal/compliance partner review not completed               |
| Native mobile app store distribution  | 5.14+       | Web-first passkey hardening before native distribution      |

## Partial capability limits (5.13 targets)

### Native mobile passkey client (Partial)

**Included:** Native mobile passkey client run audit, org-scoped status/list endpoints, admin-gated start from approved mobile passkey readiness runs.

**Not included:** App store distribution, device attestation rollout, passwordless enforcement without operator gates.

### OAuth marketplace publishing (Partial)

**Included:** Marketplace publishing run audit, org-scoped status/list endpoints, admin-gated start from approved OAuth developer apps.

**Not included:** Public marketplace listings, unreviewed third-party access approvals, automated partner trust scoring.

### Fully autonomous bureau API filing (Partial)

**Included:** Fully autonomous bureau API filing run audit, org-scoped status/list endpoints, operator-gated execute from filed autonomous bureau filing runs, admin approve.

**Not included:** Unsupervised live bureau submission loops, automatic retries without operator review, direct external filing without audit gates.

### Unredacted cross-org benchmark export (Partial)

**Included:** Unredacted export run audit, org-scoped status/list endpoints, admin-gated submit from completed cross-org benchmark refresh runs, admin/owner approve.

**Not included:** Live CSV/JSON/blob generation, raw tenant PII export, unrestricted cross-tenant data dumps.

## Related documents

- [Version 5.13 completion checklist](../development/version-5.13-completion-checklist.md)
- [Version 5.12 scope](version-5.12-scope.md)
- [Capability matrix](capability-matrix.md)
- [Release notes — v5.13.0](../release-notes/v5.13.0.md)
- [Product roadmap](../roadmap/README.md)
