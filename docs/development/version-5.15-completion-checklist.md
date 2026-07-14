# Version 5.15 Completion Checklist

Ordered path for **Compliance Intelligence Phase 8 — Identity Theft Detection & Recovery** and follow-on distribution/governance work.

Preceded by shipped **v5.14.0**. **Released as v5.15.0.**

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

Scope: [`docs/governance/version-5.15-scope.md`](../governance/version-5.15-scope.md) · Release notes: [`docs/release-notes/v5.15.0.md`](../release-notes/v5.15.0.md)

## Exit criteria for "5.15 done"

- [x] Identity Theft Detection & Recovery Engine is core (not optional) in Compliance Intelligence
- [x] Consumer confirmation + attestation required before confirmed identity-theft claims / §605B path
- [x] Ordinary dispute generation paused for locked accounts
- [x] Capability matrix + API reference updated
- [x] Deferred items explicitly documented

---

## Phase 1 — Recommended order

| Order | Slice                                                | Epic                    | Status |
| ----- | ---------------------------------------------------- | ----------------------- | ------ |
| 1     | 5.15 scope + completion checklist                    | Kickoff                 | ✅     |
| 2     | Identity Theft Detection & Recovery Engine (Phase 8) | Compliance Intelligence | ✅     |
| 3     | Portal consumer confirmation / attestation           | Client Experience       | ✅     |
| 4     | §605B packet export / bureau block letters           | Disputes                | ✅     |
| 5     | Capability matrix 5.15 sign-off                      | Governance              | ✅     |

---

## Explicitly not 5.15 (→ 5.16+)

| Capability                                      | Version | Why defer                                          |
| ----------------------------------------------- | ------- | -------------------------------------------------- |
| Unsupervised sworn ID-theft claim generation    | Never   | Requires consumer confirmation by product rule     |
| Fully unsupervised live bureau §605B submission | 5.16+   | Legal/compliance sign-off and kill-switch required |
| Unrestricted cross-tenant PII data lake export  | 5.16+   | Data governance and legal review not complete      |
| Auto-bundled evidence exhibits in §605B ZIP     | 5.16+   | Checklist tracking only in v5.15                   |
