# Version 5.9 Completion Checklist

Ordered path to **compliance-gated autonomous production**. Preceded by shipped **v5.8.0** production integration scaffolds.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for “5.9 done”

- [ ] All four epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.9-scope.md`](../governance/version-5.9-scope.md)
- [ ] Capability matrix updated for 5.9 slices
- [ ] Unsupervised loops, bureau filing, live Stripe Tax, and SAML rotation paths verified behind feature flags
- [ ] `docs/release-notes/v5.9.0.md` + tag `v5.9.0`

---

## Phase 1 — Recommended order

| Order | Slice                             | Epic          | Status |
| ----- | --------------------------------- | ------------- | ------ |
| 1     | 5.9 scope + completion checklist  | Kickoff       | ✅     |
| 2     | Agent unsupervised loop scaffold  | AI operations | —      |
| 3     | Autonomous bureau filing scaffold | Disputes      | —      |
| 4     | Live Stripe Tax API scaffold      | Billing       | —      |
| 5     | SAML automated rotation scaffold  | Identity      | —      |
| 6     | Capability matrix 5.9 sign-off    | Governance    | —      |

Slice 2 requires `ENABLE_AGENT_SUPERVISED_LOOPS=true` and a `completed` supervised loop run. Slice 3 requires `ENABLE_BUREAU_LIVE_API=true` and an `invoked` bureau live API run. Slice 4 requires `ENABLE_STRIPE_TAX_CALCULATION=true`; no live Stripe Tax API calls without compliance deferral docs. Slice 5 requires `ENABLE_SAML_CERTIFICATE_ROTATION=true` and a `rotated` SAML cert rotation run.

---

## Explicitly not 5.9 (→ 5.10+)

| Capability                    | Version | Why defer                            |
| ----------------------------- | ------- | ------------------------------------ |
| Arbitrary agent execution     | 5.10+   | After unsupervised loop scaffold     |
| Unsupervised bureau re-filing | 5.10+   | Legal/compliance beyond filing audit |
| Native mobile apps            | 5.10+   | Web-first production                 |
| Public OAuth dev portal       | 5.10+   | After internal portal stable         |
| Cross-org benchmarks          | 5.10+   | Multi-tenant policy not approved     |
| HRIS passwordless UI          | 5.10+   | After SAML rotation scaffold         |
