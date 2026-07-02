# Version 4.8 Completion Checklist

Ordered path to **v4.8.0** — **in progress**. Preceded by shipped **v4.5.0**.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for “4.8 done”

- [ ] All five epics below are **✅ or explicitly deferred to 5.0** with docs updated — see [`version-4.8-scope.md`](../governance/version-4.8-scope.md)
- [ ] Capability matrix rows for 4.8 show **✅** (or **Partial** with written scope limits)
- [ ] `v4.8.0` release notes + tag
- [x] LLM features gated behind policy ADR + `ENABLE_LLM`
- [ ] No **Planned** items remain that were promised for 4.8 in `docs/roadmap/README.md` (deferred items documented)

---

## Phase 1 — Recommended order

| Order | Slice                                        | Epic          | Status |
| ----- | -------------------------------------------- | ------------- | ------ |
| 1     | 4.8 scope + completion checklist             | Kickoff       | ✅     |
| 2     | In-app notifications model + API             | Notifications | ✅     |
| 3     | Notification center UI (staff web)           | Notifications | ✅     |
| 4     | Scheduled overdue investigation worker       | Workflow      | ✅     |
| 5     | `job-orchestrator` package scaffold + ADR    | Platform      | ✅     |
| 6     | Client + contact model                       | Client Mgmt   | ✅     |
| 7     | Client portal auth partition                 | Client Portal | ✅     |
| 8     | LLM policy ADR + provider config gates       | AI            | ✅     |
| 9     | Email delivery scaffold (feature-flagged)    | Comms         | ✅     |
| 10    | Reporting read models / dashboard expansions | Reporting     | ✅     |
| 11    | Client portal case progress view             | Client Portal | ✅     |
| 12    | Capability matrix 4.8 sign-off + deferrals   | Governance    | —      |
| 13    | `docs/release-notes/v4.8.0.md`               | Release       | —      |
| 14    | Tag `v4.8.0`                                 | Release       | —      |

LLM implementation slices (8+) require the policy ADR merged before external provider calls ship.

---

## Explicitly not 4.8 (→ 5.0)

| Capability              | Version | Why defer  |
| ----------------------- | ------- | ---------- |
| SSO / MFA               | 5.0     | Enterprise |
| Compliance center       | 5.0     | Legal      |
| Autonomous dispute file | 5.0+    | Compliance |
| Full BPM designer       | 5.0     | Scale      |
