# Version 5.14 Completion Checklist

Ordered path to **production distribution depth**. Preceded by shipped **v5.13.0** native mobile depth scaffolds.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for "5.14 done"

- [x] All four epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.14-scope.md`](../governance/version-5.14-scope.md)
- [x] Capability matrix updated for 5.14 slices
- [x] Live unredacted blob export, unsupervised filing loops, public marketplace listings, and app store distribution paths verified behind feature flags
- [x] `docs/release-notes/v5.14.0.md` + tag `v5.14.0`

---

## Phase 1 — Recommended order

| Order | Slice                                 | Epic       | Status |
| ----- | ------------------------------------- | ---------- | ------ |
| 1     | 5.14 scope + completion checklist     | Kickoff    | ✅     |
| 2     | Live unredacted benchmark blob export | Reporting  | ✅     |
| 3     | Unsupervised autonomous filing loops  | Disputes   | ✅     |
| 4     | Public OAuth marketplace listings     | Platform   | ✅     |
| 5     | Native mobile app store distribution  | Identity   | ✅     |
| 6     | Capability matrix 5.14 sign-off       | Governance | ✅     |

Slice 2 requires approved unredacted export runs and secure storage config. Slice 3 requires approved fully autonomous bureau API filing runs. Slice 4 requires approved OAuth marketplace publishing runs. Slice 5 requires approved native mobile passkey client runs.

---

## Explicitly not 5.14 (→ 5.15+)

| Capability                                      | Version | Why defer                                                 |
| ----------------------------------------------- | ------- | --------------------------------------------------------- |
| Unrestricted cross-tenant PII data lake export  | 5.15+   | Data governance and legal review not complete             |
| Fully unsupervised live bureau submission loops | 5.15+   | Stronger compliance controls and kill-switch required     |
| Unreviewed third-party marketplace auto-approve | 5.15+   | Partner trust scoring and legal review not complete       |
| Production App Store / Play Store release ops   | 5.15+   | Distribution readiness and signing pipeline not finalized |
