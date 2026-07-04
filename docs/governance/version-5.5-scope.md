# Version 5.5 Scope & Deferrals

Formal scope for **Version 5.5 — Production Automation**. Builds on shipped **v5.4.0** production operations scaffolds.

**Kickoff date:** 2026-07-04  
**Target:** Ship the next layer of 5.4-deferred production automation — invoice collection, SAML metadata, marketing SMS delivery worker, and human-gated agent execution — without autonomous dispute filing or native mobile apps.

## Theme

Extend partial 5.4 production operations (invoicing runs, IdP registry, marketing campaigns, agent observability) toward automated delivery paths with compliance gates. Each epic ships as a **Partial** capability behind feature flags with tests and documentation.

## Epic outcomes (planned)

| Epic | Theme                      | 5.5 outcome | Summary                                                               |
| ---- | -------------------------- | ----------- | --------------------------------------------------------------------- |
| 1    | Billing invoice collection | Partial ✅  | Stripe invoice PDF + payment collection reminder scaffold             |
| 2    | SAML federation metadata   | Partial ✅  | Per-tenant SAML metadata upload and validation scaffold               |
| 3    | Marketing SMS delivery     | Partial ✅  | Worker job to deliver queued marketing SMS campaign runs              |
| 4    | Agent execution scaffold   | Partial ✅  | Human-gated agent step execution audit (no autonomous dispute filing) |

## Shipped from 5.4 (foundation — do not regress)

All v5.4.0 APIs, feature flags, migrations, worker jobs, portal UI, and `@verdin/api-client` functions remain production capabilities. See [`version-5.4-scope.md`](version-5.4-scope.md) and [`version-5.4-completion-checklist.md`](../development/version-5.4-completion-checklist.md).

## Explicit deferrals (not 5.5)

| Capability                 | Deferred to | Reason                                          |
| -------------------------- | ----------- | ----------------------------------------------- |
| Autonomous dispute filing  | 5.6+        | Legal/compliance review beyond 5.5              |
| AI fully autonomous agents | 5.6+        | Requires agent execution scaffold in production |
| Native mobile apps         | 5.6+        | Web-first production                            |
| Public OAuth dev portal    | 5.6+        | After internal developer portal stabilizes      |
| Cross-org benchmarks       | 5.6+        | Multi-tenant analytics policy not approved      |
| LLM dispute draft augment  | 5.6+        | ADR-012 + compliance review                     |
| HRIS bidirectional sync    | 5.6+        | After SAML metadata scaffold stabilizes         |

## Partial capability limits (5.5 targets)

### Billing invoice collection (Partial)

**Included:** Stripe invoice PDF generation scaffold, payment collection reminder enqueue, org-scoped collection run audit when `ENABLE_BILLING=true`.

**Not included:** Tax calculation, dunning legal templates, automated charge retries across payment methods.

### SAML federation metadata (Partial)

**Included:** SAML metadata upload endpoint, metadata validation audit log, federation status alignment with IdP registry.

**Not included:** HRIS bidirectional sync, passwordless enrollment UI, automated certificate rotation.

### Marketing SMS delivery (Partial)

**Included:** Worker job to process `sms_marketing_campaign_runs`, Twilio send from campaign queue, delivery outcome audit.

**Not included:** Deliverability dashboards, multi-provider failover, A/B testing, opt-out compliance automation.

### Agent execution scaffold (Partial)

**Included:** Human-gated agent step execution audit table, status/list/approve endpoints, timeline correlation for staff review.

**Not included:** Autonomous dispute filing, external tool calling without approval, unsupervised agent loops.

## Related documents

- [Version 5.5 completion checklist](../development/version-5.5-completion-checklist.md)
- [Version 5.4 scope](version-5.4-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
