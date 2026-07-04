# Version 5.2 Completion Checklist

Ordered path to **deferred production surfaces** — **in progress**. Preceded by shipped **v5.1.0** production hardening.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for “5.2 done”

- [ ] All five epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.2-scope.md`](../governance/version-5.2-scope.md)
- [ ] Capability matrix updated for 5.2 slices
- [ ] Production SMS and LLM document summary paths verified behind feature flags
- [ ] `docs/release-notes/v5.2.0.md` + tag `v5.2.0`

---

## Phase 1 — Recommended order

| Order | Slice                            | Epic              | Status |
| ----- | -------------------------------- | ----------------- | ------ |
| 1     | 5.2 scope + completion checklist | Kickoff           | ✅     |
| 2     | Production SMS delivery          | Communications    | ✅     |
| 3     | LLM document summary UI          | AI                | —      |
| 4     | Web Push HTTP delivery           | Client Portal     | ✅     |
| 5     | Revenue analytics scaffold       | Billing/Reporting | ✅     |
| 6     | API key rate-limit scaffold      | API integrations  | ✅     |
| 7     | Capability matrix 5.2 sign-off   | Governance        | —      |

Slice 2 requires Twilio test credentials. Slice 3 requires `ENABLE_LLM=true` and ADR-012 gates. Slice 4 requires `ENABLE_PORTAL_PUSH` + VAPID keys. Slice 5 requires `ENABLE_BILLING` + Stripe test data.

---

## Explicitly not 5.2 (→ 5.3+)

| Capability              | Version | Why defer              |
| ----------------------- | ------- | ---------------------- |
| Autonomous dispute file | 5.3+    | Legal review           |
| SCIM provisioning       | 5.3+    | After enrollment prod  |
| Predictive analytics    | 5.3+    | Data pipeline          |
| AI autonomous agents    | 5.3+    | Observability          |
| Native mobile apps      | 5.3+    | Web-first production   |
| Billing usage metering  | 5.3+    | After revenue scaffold |
