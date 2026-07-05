# Version 5.8 Completion Checklist

Ordered path to **compliance-gated production integrations**. Preceded by shipped **v5.7.0** autonomous workflow scaffolds.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for “5.8 done”

- [ ] All four epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.8-scope.md`](../governance/version-5.8-scope.md)
- [ ] Capability matrix updated for 5.8 slices
- [ ] Supervised loops, bureau API, tax calculation, and HRIS lifecycle paths verified behind feature flags
- [ ] `docs/release-notes/v5.8.0.md` + tag `v5.8.0`

---

## Phase 1 — Recommended order

| Order | Slice                                | Epic          | Status |
| ----- | ------------------------------------ | ------------- | ------ |
| 1     | 5.8 scope + completion checklist     | Kickoff       | ✅     |
| 2     | Agent supervised loop scaffold       | AI operations | ✅     |
| 3     | Bureau live API integration scaffold | Disputes      | ✅     |
| 4     | Stripe tax calculation scaffold      | Billing       | ✅     |
| 5     | HRIS lifecycle sync scaffold         | Identity      | ✅     |
| 6     | Capability matrix 5.8 sign-off       | Governance    | —      |

Slice 2 requires `ENABLE_AGENT_EXTERNAL_TOOL_CALLING=true` and an `invoked` tool invocation run. Slice 3 requires `ENABLE_DISPUTE_BUREAU_SUBMISSION=true` and a `submitted` bureau submission run. Slice 4 requires `ENABLE_STRIPE_INVOICE_PDF=true`; no live Stripe Tax API calls without compliance deferral docs. Slice 5 requires `ENABLE_HRIS_BIDIRECTIONAL_SYNC=true`.

---

## Explicitly not 5.8 (→ 5.9+)

| Capability                | Version | Why defer                            |
| ------------------------- | ------- | ------------------------------------ |
| Fully unsupervised agents | 5.9+    | After supervised loop scaffold       |
| Autonomous bureau filing  | 5.9+    | Legal/compliance beyond API scaffold |
| Native mobile apps        | 5.9+    | Web-first production                 |
| Public OAuth dev portal   | 5.9+    | After internal portal stable         |
| Cross-org benchmarks      | 5.9+    | Multi-tenant policy not approved     |
