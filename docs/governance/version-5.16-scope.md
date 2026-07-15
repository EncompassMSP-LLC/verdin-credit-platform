# Version 5.16 Scope & Deferrals

Formal scope for **Version 5.16 — Identity-Theft Recovery Depth & §605B Evidence Bundling (Compliance Intelligence Phase 9)**. Builds on shipped **v5.15.0** Identity Theft Detection & Recovery (Phase 8).

**Kickoff date:** 2026-07-15  
**Target:** Deepen the Phase 8 engine with staff-mediated §605B evidence bundling, richer mixed-file / personal-info variation detection, an operator-gated §605B submission-readiness audit, and lock-aware dispute preparation — **without** live unsupervised bureau §605B submission or unrestricted cross-tenant PII export.

## Theme

Phase 8 established detection, consumer confirmation, the Identity Theft Case Center, and a staff-mediated §605B block packet. Phase 9 makes recovery **evidence-complete and lock-aware**: real exhibits travel with the §605B packet, mixed-file/personal-info variations surface as investigator signals (never auto-labels), packet readiness is auditable before any human submission, and ordinary dispute preparation respects identity-theft account locks. Indicators must never auto-generate sworn claims, and live bureau submission stays behind legal/compliance sign-off.

## Epic outcomes (target)

| Epic | Theme                                          | 5.16 target | Summary                                                                      |
| ---- | ---------------------------------------------- | ----------- | ---------------------------------------------------------------------------- |
| 1    | §605B evidence exhibit bundling                | Planned     | Attach stored case evidence documents into the staff-mediated §605B ZIP      |
| 2    | Mixed-file / personal-info variation detection | Planned     | Phase 9 heuristics for name/SSN/address/DOB variations across tradelines     |
| 3    | §605B submission-readiness audit               | Planned     | Operator-gated readiness run audit (completeness checks; no live submission) |
| 4    | Lock-aware dispute preparation                 | Planned     | `prepare` + strategy stages skip/annotate confirmed identity-theft locks     |
| 5    | Capability matrix / governance sign-off        | Planned     | Scope, checklist, matrix rows, release notes                                 |

## Shipped from 5.15 (foundation — do not regress)

All v5.15.0 APIs, feature flags, migrations, UI scaffolds, and `@verdin/api-client` functions remain production capabilities — Phase 8 detection, Case Center, consumer confirmation/attestation, ordinary dispute pause, and the staff-mediated §605B packet export. See [`version-5.15-scope.md`](version-5.15-scope.md).

## Explicit deferrals (not 5.16)

| Capability                                      | Deferred to | Reason                                                          |
| ----------------------------------------------- | ----------- | --------------------------------------------------------------- |
| Unsupervised sworn ID-theft claim generation    | Never       | Requires consumer confirmation by product rule                  |
| Auto-classifying mixed-file as confirmed theft  | Never       | Variation signals are advisory; confirmation stays a human gate |
| Fully unsupervised live bureau §605B submission | 5.17+       | Legal/compliance sign-off and kill-switch required              |
| Unrestricted cross-tenant PII data lake export  | 5.17+       | Data governance and legal review not complete                   |

## Partial capability limits (5.16 targets)

### §605B evidence exhibit bundling (Planned)

**Included:** Bundle staff-selected, case-scoped evidence documents into the existing `605b-packet.zip` alongside the block letters and readiness manifest; size/type gating; exhibit manifest listing what was attached.

**Not included:** Automatic (unreviewed) attachment of every case document; sending exhibits to bureaus.

### Mixed-file / personal-info variation detection (Planned)

**Included:** Heuristics detecting name, SSN, address, and DOB variations and mixed-file indicators across stored tradelines; surfaced as advisory signals in the Case Center.

**Not included:** Auto-labeling accounts as identity theft; generating sworn claims from variation signals.

### §605B submission-readiness audit (Planned)

**Included:** Operator-gated readiness run that validates confirmed theft + attestation + packet completeness and records a readiness run audit row.

**Not included:** Any live bureau API call or automated submission.

### Lock-aware dispute preparation (Planned)

**Included:** `POST /cases/{id}/dispute-strategy/prepare` and strategy stages skip or annotate accounts locked by confirmed identity theft, keeping §605B and §611 paths separate.

**Not included:** Auto-unlocking accounts; overriding the ordinary dispute pause.

## Related documents

- [Version 5.16 completion checklist](../development/version-5.16-completion-checklist.md)
- [Version 5.15 scope](version-5.15-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [API reference](../api/reference.md)
