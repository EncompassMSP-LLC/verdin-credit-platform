# Version 5.1 Completion Checklist

Ordered path to **production hardening** — **in progress**. Preceded by **5.0+ pilot-ready** sign-off.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for “5.1 done”

- [ ] All eight epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.1-scope.md`](../governance/version-5.1-scope.md)
- [ ] Capability matrix updated for 5.1 slices
- [ ] API keys authenticate on at least one production integration path
- [ ] `docs/release-notes/v5.1.0.md` + tag `v5.1.0`

---

## Phase 1 — Recommended order

| Order | Slice                             | Epic             | Status |
| ----- | --------------------------------- | ---------------- | ------ |
| 1     | 5.1 scope + completion checklist  | Kickoff          | ✅     |
| 2     | API key auth middleware           | API integrations | ✅     |
| 3     | Production SMS delivery           | Communications   | —      |
| 4     | IdP / TOTP enrollment             | Identity         | ✅     |
| 5     | Stripe billing scaffold           | Billing          | ✅     |
| 6     | Compliance enforcement jobs       | Compliance       | ✅     |
| 7     | LLM document summary UI           | AI               | —      |
| 8     | Portal push notification scaffold | Client Portal    | ✅     |
| 9     | Reporting materialized views      | Reporting        | ✅     |
| 10    | Capability matrix 5.1 sign-off    | Governance       | —      |

Slices 4+ require `ENABLE_ENTERPRISE=true`. Slice 7 requires `ENABLE_LLM=true` and ADR-012 gates. Slice 5 requires Stripe test keys in environment.

---

## Explicitly not 5.1 (→ 5.2+)

| Capability              | Version | Why defer              |
| ----------------------- | ------- | ---------------------- |
| Autonomous dispute file | 5.2+    | Legal review           |
| Predictive analytics    | 5.2+    | Data pipeline          |
| AI autonomous agents    | 5.2+    | Observability          |
| Native mobile apps      | 5.2+    | Web-first production   |
| SCIM / multi-IdP        | 5.2+    | After enrollment ships |
