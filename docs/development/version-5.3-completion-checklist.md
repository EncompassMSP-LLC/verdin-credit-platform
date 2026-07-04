# Version 5.3 Completion Checklist

Ordered path to **enterprise depth** — **in progress**. Preceded by shipped **v5.2.0** deferred production surfaces.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for “5.3 done”

- [ ] All five epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.3-scope.md`](../governance/version-5.3-scope.md)
- [ ] Capability matrix updated for 5.3 slices
- [ ] SCIM and usage metering paths verified behind feature flags
- [ ] `docs/release-notes/v5.3.0.md` + tag `v5.3.0`

---

## Phase 1 — Recommended order

| Order | Slice                            | Epic             | Status |
| ----- | -------------------------------- | ---------------- | ------ |
| 1     | 5.3 scope + completion checklist | Kickoff          | ✅     |
| 2     | Billing usage metering scaffold  | Billing          | ✅     |
| 3     | SCIM provisioning scaffold       | Identity         | ✅     |
| 4     | Predictive analytics scaffold    | Reporting / AI   | ✅     |
| 5     | API key rotation + dev portal    | API integrations | —      |
| 6     | Batch document summarization job | LLM operations   | —      |
| 7     | Capability matrix 5.3 sign-off   | Governance       | —      |

Slice 2 requires `ENABLE_BILLING=true` + Stripe test data. Slice 3 requires `ENABLE_ENTERPRISE=true` and stable OIDC enrollment. Slice 4 requires historical case/account data in test DB. Slice 6 requires `ENABLE_LLM=true` and ADR-012 gates.

---

## Explicitly not 5.3 (→ 5.4+)

| Capability              | Version | Why defer                    |
| ----------------------- | ------- | ---------------------------- |
| Autonomous dispute file | 5.4+    | Legal/compliance review      |
| AI autonomous agents    | 5.4+    | Observability prerequisites  |
| Native mobile apps      | 5.4+    | Web-first production         |
| Invoicing / dunning     | 5.4+    | After metering in production |
| Multi-IdP federation    | 5.4+    | After SCIM scaffold          |
