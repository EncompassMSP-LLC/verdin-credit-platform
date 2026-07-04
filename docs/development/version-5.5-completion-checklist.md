# Version 5.5 Completion Checklist

Ordered path to **production automation** — **in progress**. Preceded by shipped **v5.4.0** production operations.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for “5.5 done”

- [ ] All four epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.5-scope.md`](../governance/version-5.5-scope.md)
- [ ] Capability matrix updated for 5.5 slices
- [ ] Invoice collection and SAML metadata paths verified behind feature flags
- [ ] `docs/release-notes/v5.5.0.md` + tag `v5.5.0`

---

## Phase 1 — Recommended order

| Order | Slice                            | Epic           | Status |
| ----- | -------------------------------- | -------------- | ------ |
| 1     | 5.5 scope + completion checklist | Kickoff        | ✅     |
| 2     | Invoice collection scaffold      | Billing        | ✅     |
| 3     | SAML metadata upload scaffold    | Identity       | ✅     |
| 4     | Marketing SMS delivery worker    | Communications | ✅     |
| 5     | Agent execution scaffold         | AI operations  | ✅     |
| 6     | Capability matrix 5.5 sign-off   | Governance     | —      |

Slice 2 requires `ENABLE_BILLING=true` + Stripe test data. Slice 3 requires `ENABLE_ENTERPRISE=true` and IdP federation scaffold. Slice 4 requires `ENABLE_SMS_MARKETING_CAMPAIGNS=true` + Twilio credentials. Slice 5 requires `ENABLE_AI=true` and agent observability; no autonomous dispute filing without compliance deferral docs.

---

## Explicitly not 5.5 (→ 5.6+)

| Capability              | Version | Why defer                    |
| ----------------------- | ------- | ---------------------------- |
| Autonomous dispute file | 5.6+    | Legal/compliance review      |
| Fully autonomous agents | 5.6+    | After human-gated execution  |
| Native mobile apps      | 5.6+    | Web-first production         |
| Public OAuth dev portal | 5.6+    | After internal portal stable |
| LLM dispute augment     | 5.6+    | ADR-012 + compliance review  |
