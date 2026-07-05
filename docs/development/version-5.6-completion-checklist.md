# Version 5.6 Completion Checklist

Ordered path to **compliance-reviewed production depth**. Preceded by shipped **v5.5.0** production automation.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for “5.6 done”

- [ ] All four epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.6-scope.md`](../governance/version-5.6-scope.md)
- [ ] Capability matrix updated for 5.6 slices
- [ ] HRIS sync, deliverability, LLM augment, and filing prep paths verified behind feature flags
- [ ] `docs/release-notes/v5.6.0.md` + tag `v5.6.0`

---

## Phase 1 — Recommended order

| Order | Slice                              | Epic           | Status |
| ----- | ---------------------------------- | -------------- | ------ |
| 1     | 5.6 scope + completion checklist   | Kickoff        | ✅     |
| 2     | HRIS bidirectional sync scaffold   | Identity       | ✅     |
| 3     | SMS deliverability dashboard       | Communications | —      |
| 4     | LLM dispute draft augment scaffold | AI assistance  | —      |
| 5     | Dispute filing prep scaffold       | Disputes       | —      |
| 6     | Capability matrix 5.6 sign-off     | Governance     | —      |

Slice 2 requires `ENABLE_ENTERPRISE=true` and SAML metadata scaffold. Slice 3 requires `ENABLE_SMS_MARKETING_DELIVERY=true` and delivery logs. Slice 4 requires `ENABLE_LLM=true` and ADR-012 gates; no provider calls without scrub config. Slice 5 requires human-gated agent execution; no autonomous bureau filing without compliance deferral docs.

---

## Explicitly not 5.6 (→ 5.7+)

| Capability              | Version | Why defer                    |
| ----------------------- | ------- | ---------------------------- |
| Autonomous dispute file | 5.7+    | Legal/compliance review      |
| Fully autonomous agents | 5.7+    | After filing prep scaffold   |
| Native mobile apps      | 5.7+    | Web-first production         |
| Public OAuth dev portal | 5.7+    | After internal portal stable |
| Stripe PDF + tax calc   | 5.7+    | After collection stabilizes  |
