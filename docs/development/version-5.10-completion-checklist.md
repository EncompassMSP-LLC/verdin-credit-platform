# Version 5.10 Completion Checklist

Ordered path to **compliance-gated production automation**. Preceded by shipped **v5.9.0** autonomous production scaffolds.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for “5.10 done”

- [ ] All four epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.10-scope.md`](../governance/version-5.10-scope.md)
- [ ] Capability matrix updated for 5.10 slices
- [ ] Arbitrary execution, bureau re-filing, charge retry, and passwordless enrollment paths verified behind feature flags
- [ ] `docs/release-notes/v5.10.0.md` + tag `v5.10.0`

---

## Phase 1 — Recommended order

| Order | Slice                                 | Epic          | Status |
| ----- | ------------------------------------- | ------------- | ------ |
| 1     | 5.10 scope + completion checklist     | Kickoff       | ✅     |
| 2     | Agent arbitrary execution scaffold    | AI operations | ✅     |
| 3     | Bureau re-filing audit scaffold       | Disputes      | ✅     |
| 4     | Stripe charge retry scaffold          | Billing       | ✅     |
| 5     | SAML passwordless enrollment scaffold | Identity      | —      |
| 6     | Capability matrix 5.10 sign-off       | Governance    | —      |

Slice 2 requires `ENABLE_AGENT_UNSUPERVISED_LOOPS=true` and an `approved` unsupervised loop run. Slice 3 requires `ENABLE_AUTONOMOUS_BUREAU_FILING=true` and an `approved` autonomous filing run. Slice 4 requires `ENABLE_STRIPE_LIVE_TAX_API=true`; no live charge retries without compliance deferral docs. Slice 5 requires `ENABLE_SAML_AUTOMATED_ROTATION=true` and an `automated` SAML automated rotation run.

---

## Explicitly not 5.10 (→ 5.11+)

| Capability                  | Version | Why defer                               |
| --------------------------- | ------- | --------------------------------------- |
| Unsupervised re-filing      | 5.11+   | Legal/compliance beyond re-filing audit |
| Live charge retries         | 5.11+   | After charge retry scaffold stabilizes  |
| Native mobile apps          | 5.11+   | Web-first production                    |
| Public OAuth dev portal     | 5.11+   | After internal portal stable            |
| Cross-org benchmarks        | 5.11+   | Multi-tenant policy not approved        |
| HRIS passwordless UI        | 5.11+   | After SAML passwordless scaffold        |
| Multi-IdP bulk provisioning | 5.11+   | After passwordless enrollment scaffold  |
