# Version 5.4 Completion Checklist

Ordered path to **production operations** — **in progress**. Preceded by shipped **v5.3.0** enterprise depth.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for “5.4 done”

- [ ] All four epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.4-scope.md`](../governance/version-5.4-scope.md)
- [ ] Capability matrix updated for 5.4 slices
- [ ] Invoicing and federation paths verified behind feature flags
- [ ] `docs/release-notes/v5.4.0.md` + tag `v5.4.0`

---

## Phase 1 — Recommended order

| Order | Slice                            | Epic           | Status |
| ----- | -------------------------------- | -------------- | ------ |
| 1     | 5.4 scope + completion checklist | Kickoff        | ✅     |
| 2     | Invoicing & dunning scaffold     | Billing        | ✅     |
| 3     | Multi-IdP federation scaffold    | Identity       | ✅     |
| 4     | Marketing SMS campaigns scaffold | Communications | ✅     |
| 5     | Agent observability scaffold     | AI operations  | ✅     |
| 6     | Capability matrix 5.4 sign-off   | Governance     | —      |

Slice 2 requires `ENABLE_BILLING=true` + Stripe test data. Slice 3 requires `ENABLE_ENTERPRISE=true` and SCIM scaffold. Slice 4 requires `ENABLE_SMS_DELIVERY=true` + Twilio test credentials. Slice 5 requires `ENABLE_AI=true`; no external LLM calls without ADR-012 gates.

---

## Explicitly not 5.4 (→ 5.5+)

| Capability              | Version | Why defer                     |
| ----------------------- | ------- | ----------------------------- |
| Autonomous dispute file | 5.5+    | Legal/compliance review       |
| AI autonomous agents    | 5.5+    | Execution after observability |
| Native mobile apps      | 5.5+    | Web-first production          |
| Public OAuth dev portal | 5.5+    | After internal portal stable  |
| LLM dispute augment     | 5.5+    | ADR-012 + compliance review   |
