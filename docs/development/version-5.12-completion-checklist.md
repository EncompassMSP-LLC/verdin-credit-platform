# Version 5.12 Completion Checklist

Ordered path to **compliance-gated expansion surfaces**. Preceded by shipped **v5.11.0** production execution scaffolds.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for "5.12 done"

- [ ] All four epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.12-scope.md`](../governance/version-5.12-scope.md)
- [ ] Capability matrix updated for 5.12 slices
- [ ] Bureau live API invocation, public OAuth developer portal, cross-org benchmark analytics, and mobile passkey readiness paths verified behind feature flags
- [ ] `docs/release-notes/v5.12.0.md` + tag `v5.12.0`

---

## Phase 1 — Recommended order

| Order | Slice                                  | Epic       | Status |
| ----- | -------------------------------------- | ---------- | ------ |
| 1     | 5.12 scope + completion checklist      | Kickoff    | ✅     |
| 2     | Bureau live API invocation scaffold    | Disputes   | —      |
| 3     | Public OAuth developer portal scaffold | Platform   | —      |
| 4     | Cross-org benchmark analytics scaffold | Reporting  | —      |
| 5     | Mobile passkey readiness scaffold      | Identity   | —      |
| 6     | Capability matrix 5.12 sign-off        | Governance | —      |

Slice 2 requires the prior filing-prep/filing workflow gate to be enabled and an approved source run. Slice 3 requires enterprise identity and API key governance scaffolds enabled. Slice 4 requires governance-approved aggregate benchmark sources. Slice 5 requires passkey readiness gates and approved identity enrollment prerequisites.

---

## Explicitly not 5.12 (→ 5.13+)

| Capability                            | Version | Why defer                                         |
| ------------------------------------- | ------- | ------------------------------------------------- |
| Fully autonomous bureau API filing    | 5.13+   | Needs stronger compliance controls                |
| OAuth marketplace ecosystem           | 5.13+   | Legal/compliance and partner review not completed |
| Native mobile applications            | 5.13+   | Web-first readiness and passkey hardening first   |
| Unredacted cross-org benchmark export | 5.13+   | Data governance policy not fully approved         |
