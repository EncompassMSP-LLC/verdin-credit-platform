# Version 5.13 Completion Checklist

Ordered path to **native mobile depth and deferred 5.12 expansion surfaces**. Preceded by shipped **v5.12.0** compliance-gated expansion scaffolds.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for "5.13 done"

- [ ] All four epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.13-scope.md`](../governance/version-5.13-scope.md) (create at sign-off)
- [x] Capability matrix updated for 5.13 slices
- [ ] Native mobile passkey client, OAuth marketplace publishing, fully autonomous bureau API filing, and unredacted benchmark export paths verified behind feature flags
- [ ] `docs/release-notes/v5.13.0.md` + tag `v5.13.0`

---

## Phase 1 — Recommended order

| Order | Slice                                       | Epic       | Status |
| ----- | ------------------------------------------- | ---------- | ------ |
| 1     | Native mobile passkey client scaffold       | Identity   | ✅     |
| 2     | OAuth marketplace publishing scaffold       | Platform   | ✅     |
| 3     | Fully autonomous bureau API filing scaffold | Disputes   | ✅     |
| 4     | Unredacted cross-org benchmark export       | Reporting  | ✅     |
| 5     | Capability matrix 5.13 sign-off             | Governance | —      |

Slice 1 requires mobile passkey readiness gates. Slice 2 requires public OAuth developer portal and approved OAuth apps. Slice 3 requires filed autonomous bureau filing runs. Slice 4 requires completed cross-org benchmark refresh runs and governance-approved export policy.

---

## Explicitly not 5.13 (→ 5.14+)

| Capability                            | Version | Why defer                                            |
| ------------------------------------- | ------- | ---------------------------------------------------- |
| Live unredacted benchmark blob export | 5.14+   | Data governance and secure export pipeline not built |
| Unsupervised autonomous filing loops  | 5.14+   | Stronger compliance controls required                |
| Public OAuth marketplace listings     | 5.14+   | Legal/compliance partner review not completed        |
| Native mobile app store distribution  | 5.14+   | Web-first passkey hardening first                    |
