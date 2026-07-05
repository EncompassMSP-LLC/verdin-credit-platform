# Version 5.7 Completion Checklist

Ordered path to **compliance-gated autonomous workflows**. Preceded by shipped **v5.6.0** compliance-reviewed production depth.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for “5.7 done”

- [ ] All four epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.7-scope.md`](../governance/version-5.7-scope.md)
- [ ] Capability matrix updated for 5.7 slices
- [ ] Bureau submission, tool-calling, cert rotation, and invoice PDF paths verified behind feature flags
- [ ] `docs/release-notes/v5.7.0.md` + tag `v5.7.0`

---

## Phase 1 — Recommended order

| Order | Slice                                | Epic          | Status |
| ----- | ------------------------------------ | ------------- | ------ |
| 1     | 5.7 scope + completion checklist     | Kickoff       | ✅     |
| 2     | Dispute bureau submission scaffold   | Disputes      | ✅     |
| 3     | Agent external tool-calling scaffold | AI operations | ✅     |
| 4     | SAML certificate rotation scaffold   | Identity      | ✅     |
| 5     | Stripe invoice PDF scaffold          | Billing       | ✅     |
| 6     | Capability matrix 5.7 sign-off       | Governance    | —      |

Slice 2 requires `ENABLE_DISPUTE_FILING_PREP=true` and a `prepared` filing prep run. Slice 3 requires `ENABLE_AGENT_EXECUTION=true`. Slice 4 requires `ENABLE_HRIS_BIDIRECTIONAL_SYNC=true` and SAML metadata scaffold. Slice 5 requires `ENABLE_BILLING_INVOICE_COLLECTION=true`; no live Stripe PDF API calls without compliance deferral docs.

---

## Explicitly not 5.7 (→ 5.8+)

| Capability                | Version | Why defer                        |
| ------------------------- | ------- | -------------------------------- |
| Fully unsupervised agents | 5.8+    | After tool-calling scaffold      |
| Autonomous bureau filing  | 5.8+    | Legal/compliance beyond scaffold |
| Native mobile apps        | 5.8+    | Web-first production             |
| Public OAuth dev portal   | 5.8+    | After internal portal stable     |
| Stripe tax calculation    | 5.8+    | After invoice PDF scaffold       |
