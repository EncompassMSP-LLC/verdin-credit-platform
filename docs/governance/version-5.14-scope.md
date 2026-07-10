# Version 5.14 Scope & Deferrals

Formal scope for **Version 5.14 — Production Distribution Depth**. Builds on shipped **v5.13.0** native mobile depth scaffolds.

**Kickoff date:** 2026-07-10  
**Target:** Ship the next layer of 5.13-deferred production depth — live unredacted benchmark export pipeline scaffold, unsupervised autonomous filing loop audit, public OAuth marketplace listing scaffold, and native mobile app store distribution readiness — without unsupervised live bureau submission, unrestricted PII dumps, or unreviewed public marketplace publishing.

## Theme

Extend partial 5.13 operator-gated scaffolds (native passkey client, marketplace publishing audit, fully autonomous API filing audit, unredacted export audit) toward controlled distribution and live export surfaces. Each epic ships as a **Partial** capability behind feature flags with tests and documentation.

## Epic outcomes (Partial ✅)

| Epic | Theme                                 | 5.14 outcome | Summary                                                                      |
| ---- | ------------------------------------- | ------------ | ---------------------------------------------------------------------------- |
| 1    | Live unredacted benchmark blob export | Partial ✅   | Secure export pipeline scaffold from approved unredacted export audit runs   |
| 2    | Unsupervised autonomous filing loops  | Partial ✅   | Operator-gated unsupervised filing loop audit from fully autonomous API runs |
| 3    | Public OAuth marketplace listings     | Partial ✅   | Public listing publish scaffold from approved marketplace publishing runs    |
| 4    | Native mobile app store distribution  | Partial ✅   | App store distribution readiness audit from native passkey client runs       |

## Shipped from 5.13 (foundation — do not regress)

All v5.13.0 APIs, feature flags, migrations, UI scaffolds, and `@verdin/api-client` functions remain production capabilities. See [`version-5.13-scope.md`](version-5.13-scope.md) and [`version-5.13-completion-checklist.md`](../development/version-5.13-completion-checklist.md).

## Explicit deferrals (not 5.14)

| Capability                                      | Deferred to | Reason                                                    |
| ----------------------------------------------- | ----------- | --------------------------------------------------------- |
| Unrestricted cross-tenant PII data lake export  | 5.15+       | Data governance and legal review not complete             |
| Fully unsupervised live bureau submission loops | 5.15+       | Stronger compliance controls and kill-switch required     |
| Unreviewed third-party marketplace auto-approve | 5.15+       | Partner trust scoring and legal review not complete       |
| Production App Store / Play Store release ops   | 5.15+       | Distribution readiness and signing pipeline not finalized |

## Partial capability limits (5.14 targets)

### Live unredacted benchmark blob export (Partial)

**Included:** Export artifact run audit, org-scoped status/list endpoints, admin-gated start from approved unredacted export runs, secure storage reference recording.

**Not included:** Unrestricted cross-tenant PII dumps, public download links without auth, automated bulk export without operator approval.

### Unsupervised autonomous filing loops (Partial)

**Included:** Unsupervised filing loop run audit, org-scoped status/list endpoints, operator-gated start from approved fully autonomous bureau API filing runs.

**Not included:** Fully unsupervised live bureau submission without kill-switch, automatic retries without operator review windows.

### Public OAuth marketplace listings (Partial)

**Included:** Public listing publish run audit, org-scoped status/list endpoints, admin-gated start from approved OAuth marketplace publishing runs.

**Not included:** Unreviewed third-party auto-approve, automated partner trust scoring, unrestricted public API key issuance.

### Native mobile app store distribution (Partial)

**Included:** App store distribution readiness run audit, org-scoped status/list endpoints, admin-gated start from approved native mobile passkey client runs.

**Not included:** Production App Store / Play Store release operations, device attestation enforcement without operator gates.

## Related documents

- [Version 5.14 completion checklist](../development/version-5.14-completion-checklist.md)
- [Version 5.13 scope](version-5.13-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
