# Version 5.16 Completion Checklist

Ordered path for **Compliance Intelligence Phase 9 — Identity-Theft Recovery Depth & §605B Evidence Bundling** and follow-on governance work.

Preceded by shipped **v5.15.0**. **Targeting v5.16.0.**

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-5.16-scope.md`](../governance/version-5.16-scope.md)

## Exit criteria for "5.16 done"

- [x] §605B evidence exhibits bundle into the staff-mediated packet (no unreviewed auto-attach)
- [ ] Mixed-file / personal-info variation signals surface as advisory Case Center findings (never auto-label)
- [ ] §605B submission readiness is auditable behind an operator gate (no live bureau submission)
- [ ] Ordinary dispute preparation is lock-aware for confirmed identity-theft accounts
- [ ] Capability matrix + API reference updated
- [ ] Deferred items explicitly documented
- [ ] `docs/release-notes/v5.16.0.md` + tag `v5.16.0`

---

## Phase 1 — Recommended order

| Order | Slice                                          | Epic                    | Status |
| ----- | ---------------------------------------------- | ----------------------- | ------ |
| 1     | 5.16 scope + completion checklist              | Kickoff                 | ✅     |
| 2     | §605B evidence exhibit bundling                | Disputes                | ✅     |
| 3     | Mixed-file / personal-info variation detection | Compliance Intelligence | ⬜     |
| 4     | §605B submission-readiness audit               | Disputes                | ⬜     |
| 5     | Lock-aware dispute preparation                 | Disputes                | ⬜     |
| 6     | Capability matrix 5.16 sign-off                | Governance              | ⬜     |

Slice 2 requires confirmed identity-theft + staff-selected case evidence documents. Slice 3 surfaces advisory signals only. Slice 4 requires confirmed theft, attestation, and a complete packet before recording a readiness run. Slice 5 reuses the Phase 8 account-lock state.

---

## Explicitly not 5.16 (→ 5.17+)

| Capability                                      | Version | Why defer                                           |
| ----------------------------------------------- | ------- | --------------------------------------------------- |
| Unsupervised sworn ID-theft claim generation    | Never   | Requires consumer confirmation by product rule      |
| Auto-classifying mixed-file as confirmed theft  | Never   | Variation signals stay advisory; confirmation human |
| Fully unsupervised live bureau §605B submission | 5.17+   | Legal/compliance sign-off and kill-switch required  |
| Unrestricted cross-tenant PII data lake export  | 5.17+   | Data governance and legal review not complete       |
