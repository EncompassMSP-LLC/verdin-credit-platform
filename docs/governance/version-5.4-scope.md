# Version 5.4 Scope & Deferrals

Formal scope for **Version 5.4 — Production Operations**. Builds on shipped **v5.3.0** enterprise depth.

**Kickoff date:** 2026-07-04  
**Target:** Ship scaffolds for 5.3-deferred production operations — invoicing/dunning, multi-IdP federation, marketing SMS, and agent observability — without autonomous dispute filing or native mobile apps.

## Theme

Extend partial 5.3 enterprise foundations (usage metering, SCIM, predictive analytics, developer portal, batch LLM) toward operator-ready production workflows. Each epic ships as a **Partial** capability behind feature flags with tests and documentation.

## Epic outcomes (shipped)

| Epic | Theme                    | 5.4 outcome | Summary                                                         |
| ---- | ------------------------ | ----------- | --------------------------------------------------------------- |
| 1    | Billing invoicing        | Partial ✅  | Org-scoped invoice/dunning scaffold + staff read endpoints      |
| 2    | Identity federation      | Partial ✅  | Multi-IdP federation config scaffold behind enterprise gate     |
| 3    | Communications marketing | Partial ✅  | Marketing SMS campaign enqueue scaffold with delivery audit     |
| 4    | AI agent observability   | Partial ✅  | Agent run audit log + status/read endpoints (no autonomous run) |

## Shipped from 5.3 (foundation — do not regress)

All v5.3.0 APIs, feature flags, migrations, worker jobs, portal UI, and `@verdin/api-client` functions remain production capabilities. See [`version-5.3-scope.md`](version-5.3-scope.md) and [`version-5.3-completion-checklist.md`](../development/version-5.3-completion-checklist.md).

## Explicit deferrals (not 5.4)

| Capability                | Deferred to | Reason                                          |
| ------------------------- | ----------- | ----------------------------------------------- |
| Autonomous dispute filing | 5.5+        | Legal/compliance review beyond 5.4              |
| AI autonomous agents      | 5.5+        | Human-in-the-loop execution after observability |
| Native mobile apps        | 5.5+        | Web-first production                            |
| Public OAuth dev portal   | 5.5+        | After internal developer portal stabilizes      |
| Cross-org benchmarks      | 5.5+        | Multi-tenant analytics policy not approved      |
| LLM dispute draft augment | 5.5+        | ADR-012 + compliance review                     |

## Partial capability limits (5.4 targets)

### Billing invoicing (Partial)

**Included:** Invoice/dunning run audit table, org-scoped invoice summary read endpoint, dunning reminder enqueue scaffold when `ENABLE_BILLING=true`.

**Not included:** Stripe invoice PDF generation, payment collection automation, tax calculation.

### Identity federation (Partial)

**Included:** Multi-IdP provider registry scaffold, federation status endpoint, provision audit alignment with SCIM logs.

**Not included:** HRIS bidirectional sync, passwordless enrollment UI, per-tenant SAML metadata upload.

### Communications marketing (Partial)

**Included:** Marketing SMS campaign enqueue scaffold, campaign delivery audit log behind `ENABLE_SMS_DELIVERY`.

**Not included:** Deliverability dashboards, multi-provider failover, A/B testing.

### AI agent observability (Partial)

**Included:** Agent run audit table, `GET` status and run-list endpoints, timeline correlation for staff review.

**Not included:** Autonomous agent execution, external tool calling, dispute filing automation.

## Related documents

- [Version 5.4 completion checklist](../development/version-5.4-completion-checklist.md)
- [Version 5.3 scope](version-5.3-scope.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
