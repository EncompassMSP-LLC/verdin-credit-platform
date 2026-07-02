# Version 5.0 Completion Checklist

Ordered path to **v5.0.0** — **in progress**. Preceded by shipped **v4.8.0**.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for “5.0 done”

- [ ] All nine epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.0-scope.md`](../governance/version-5.0-scope.md)
- [ ] Capability matrix rows for 5.0 show **✅** (or **Partial** with written scope limits)
- [ ] `v5.0.0` release notes + tag
- [ ] LLM summary endpoints respect ADR-012 gates (`ENABLE_LLM`, PII policy)
- [ ] No **Planned** items remain that were promised for 5.0 in `docs/roadmap/README.md` without deferral docs

---

## Phase 1 — Recommended order

| Order | Slice                                         | Epic             | Status |
| ----- | --------------------------------------------- | ---------------- | ------ |
| 1     | 5.0 scope + completion checklist              | Kickoff          | ✅     |
| 2     | `cases.client_id` FK + staff/portal linking   | Client Mgmt      | ✅     |
| 3     | Production email delivery (provider adapters) | Communications   | —      |
| 4     | LLM case summary endpoint (post-gate)         | AI               | —      |
| 5     | Job orchestrator runner wiring + overdue cron | Platform         | —      |
| 6     | MFA / SSO foundation (feature-flagged)        | Enterprise Id    | —      |
| 7     | Compliance center scaffold + consent model    | Compliance       | —      |
| 8     | Portal document upload                        | Client Portal    | —      |
| 9     | Portal secure messaging scaffold              | Client Portal    | —      |
| 10    | Enterprise reporting read models              | Reporting        | —      |
| 11    | API keys + org admin scaffold                 | Enterprise Admin | —      |
| 12    | Capability matrix 5.0 sign-off + deferrals    | Governance       | —      |
| 13    | `docs/release-notes/v5.0.0.md`                | Release          | —      |
| 14    | Tag `v5.0.0`                                  | Release          | —      |

Slices 4+ require ADR-012 (`ENABLE_LLM`) — already merged in 4.8. External LLM calls must pass `require_llm_ready()`.

---

## Explicitly not 5.0 (→ 5.0+ / 5.1)

| Capability              | Version | Why defer         |
| ----------------------- | ------- | ----------------- |
| Autonomous dispute file | 5.0+    | Compliance        |
| Full BPM designer       | 5.0+    | Scale             |
| Billing / Stripe        | 5.1+    | Product + finance |
| Predictive analytics    | 5.1+    | Data pipeline     |
| AI autonomous agents    | 5.1+    | Compliance        |
