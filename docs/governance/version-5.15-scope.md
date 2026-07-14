# Version 5.15 Scope & Deferrals

Formal scope for **Version 5.15 — Identity Theft Detection & Recovery (Compliance Intelligence Phase 8)**. Builds on shipped **v5.14.0** production distribution depth.

**Kickoff date:** 2026-07-14  
**Target:** Ship Phase 8 as a core Compliance Intelligence Engine component — report/tradeline detection, consumer confirmation + attestation gates, Identity Theft Case Center, ordinary dispute pause, and staff-mediated FCRA §605B block packet export — without unsupervised sworn claims or live bureau §605B submission.

## Theme

Identity theft changes legal workflow, evidence, letter types, and remedy. Indicators must never auto-label accounts or generate sworn claims without consumer confirmation. §605B blocking remains separate from ordinary FCRA §611 disputes.

## Epic outcomes (Partial ✅ / Shipped ✅)

| Epic | Theme                                      | 5.15 outcome | Summary                                                              |
| ---- | ------------------------------------------ | ------------ | -------------------------------------------------------------------- |
| 1    | Identity Theft Detection & Recovery Engine | Shipped ✅   | Phase 8 rules, Case Center persistence, dispute pause, staff APIs/UI |
| 2    | Portal consumer confirmation / attestation | Shipped ✅   | Portal-scoped confirm + attestation reuse of Phase 8 gates           |
| 3    | §605B packet export / bureau block letters | Partial ✅   | Staff-mediated ZIP letters + readiness manifest; no bureau API calls |
| 4    | Capability matrix / governance sign-off    | Shipped ✅   | Scope, checklist, matrix row, release notes                          |

## Shipped from 5.14 (foundation — do not regress)

All v5.14.0 APIs, feature flags, migrations, UI scaffolds, and `@verdin/api-client` functions remain production capabilities. See [`version-5.14-scope.md`](version-5.14-scope.md).

## Explicit deferrals (not 5.15)

| Capability                                      | Deferred to | Reason                                                   |
| ----------------------------------------------- | ----------- | -------------------------------------------------------- |
| Unsupervised sworn ID-theft claim generation    | Never       | Requires consumer confirmation by product rule           |
| Fully unsupervised live bureau §605B submission | 5.16+       | Legal/compliance sign-off and kill-switch required       |
| Unrestricted cross-tenant PII data lake export  | 5.16+       | Data governance and legal review not complete            |
| Auto-bundled evidence exhibits in §605B ZIP     | 5.16+       | Checklist tracking only in v5.15; storage bundling later |

## Partial capability limits (5.15 targets)

### Identity Theft Detection & Recovery Engine (Shipped)

**Included:** Report-level fraud-alert/freeze/victim-statement detection; tradeline heuristics; Case Center (incident, reviews, protections); consumer confirmation choices; attestation required for `identity_theft`; ordinary dispute letter `409` while locked; staff Case Center UI.

**Not included:** Auto-labeling accounts as identity theft; generating sworn claims without attestation.

### Portal consumer confirmation (Shipped)

**Included:** Portal GET center + POST account-review confirmation with portal case scoping and attestation gate.

**Not included:** Portal write APIs for protections/incident admin fields.

### §605B packet export (Partial)

**Included:** `GET /cases/{id}/identity-theft/605b-packet.zip` after confirmed theft; per-bureau block letters citing §605B; readiness README; Case Center download.

**Not included:** Live bureau submission; automatic evidence document attachment into the ZIP.

## Related documents

- [Version 5.15 completion checklist](../development/version-5.15-completion-checklist.md)
- [Version 5.14 scope](version-5.14-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
