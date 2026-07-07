# Version 5.11 Completion Checklist

Ordered path to **compliance-gated production execution**. Preceded by shipped **v5.10.0** production automation scaffolds.

Linked from [`docs/roadmap/README.md`](../roadmap/README.md).

## Exit criteria for “5.11 done”

- [x] All four epics below are **✅ or explicitly deferred** with docs updated — see [`version-5.11-scope.md`](../governance/version-5.11-scope.md)
- [x] Capability matrix updated for 5.11 slices
- [x] Unsupervised re-filing, live charge retry execution, HRIS passwordless UI, and bulk provisioning paths verified behind feature flags
- [x] `docs/release-notes/v5.11.0.md` + tag `v5.11.0`

---

## Phase 1 — Recommended order

| Order | Slice                                  | Epic       | Status |
| ----- | -------------------------------------- | ---------- | ------ |
| 1     | 5.11 scope + completion checklist      | Kickoff    | ✅     |
| 2     | Unsupervised bureau re-filing scaffold | Disputes   | ✅     |
| 3     | Live charge retry execution scaffold   | Billing    | ✅     |
| 4     | HRIS passwordless UI scaffold          | Identity   | ✅     |
| 5     | Multi-IdP bulk provisioning scaffold   | Enterprise | ✅     |
| 6     | Capability matrix 5.11 sign-off        | Governance | ✅     |

Slice 2 requires `ENABLE_BUREAU_REFILING=true` and a `refiled` bureau re-filing run. Slice 3 requires `ENABLE_STRIPE_CHARGE_RETRY=true` and a `retried` charge retry run. Slice 4 requires `ENABLE_SAML_PASSWORDLESS_ENROLLMENT=true` and an `enrolled` passwordless enrollment run. Slice 5 requires `ENABLE_HRIS_PASSWORDLESS_UI=true` and an approved HRIS passwordless UI run.

---

## Explicitly not 5.11 (→ 5.12+)

| Capability               | Version | Why defer                               |
| ------------------------ | ------- | --------------------------------------- |
| Native mobile apps       | 5.12+   | Web-first production                    |
| Public OAuth dev portal  | 5.12+   | After internal portal stable            |
| Cross-org benchmarks     | 5.12+   | Multi-tenant policy not approved        |
| Live bureau API calls    | 5.12+   | After unsupervised re-filing stabilizes |
| PII export without scrub | 5.12+   | Compliance policy ADR not approved      |
