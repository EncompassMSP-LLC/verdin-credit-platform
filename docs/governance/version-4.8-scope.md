# Version 4.8 Scope & Deferrals

Formal scope for **Version 4.8 — Operations**. Builds on the shipped **v4.5.0** Automation Platform.

**Kickoff date:** 2026-07-01  
**Target tag:** `v4.8.0`

## Theme

Operations at scale: staff notifications, scheduled workflow jobs, client management foundation, client portal, LLM assistance (gated), and reporting expansions.

## Epic outcomes (planned)

| Epic | Theme               | v4.8.0 target | Summary                                                                   |
| ---- | ------------------- | ------------- | ------------------------------------------------------------------------- |
| 1    | Notifications       | Partial       | In-app notifications + center UI; email/SMS delivery scaffold             |
| 2    | Workflow Operations | Partial       | Scheduled overdue jobs; `job-orchestrator` evaluation                     |
| 3    | Client Experience   | Partial       | Client/contact model; portal auth partition; read-only progress view      |
| 4    | AI Assistance (LLM) | Partial       | Policy ADR + provider config; case/document summaries behind feature flag |
| 5    | Reporting           | Partial       | Read-optimized reporting views; dashboard expansions                      |

## Shipped from 4.5 (foundation — do not regress)

Credit report import, dispute letter lifecycle, workflow auto-tasks, rules-based intelligence, and E2E import → dispute path remain production capabilities.

## Explicit deferrals (still not 4.8)

| Capability                         | Deferred to | Reason                                    |
| ---------------------------------- | ----------- | ----------------------------------------- |
| SSO / MFA                          | 5.0         | Enterprise edition                        |
| Compliance center / consent engine | 5.0         | Legal + enterprise                        |
| Autonomous dispute filing          | 5.0+        | Compliance gates                          |
| Full BPM workflow designer         | 5.0         | Operations scale beyond 4.8 partial scope |
| Multi-tenant billing               | 5.0         | Enterprise admin                          |

## Partial capability limits (4.8 targets)

### Notifications (Partial)

**Included:** Persisted in-app notifications per user, unread count, mark read, staff notification center UI.

**Not included:** Production email/SMS delivery (scaffold only), client-facing push, WebSocket live feed.

### Workflow Operations (Partial)

**Included:** Worker job for overdue CRA investigation escalation (replaces 4.5 read-time check).

**Not included:** Generic cron scheduler UI, cross-org SLA dashboards, full `packages/job-orchestrator/` parity.

### Client Experience (Partial)

**Included:** Client and contact entities, portal auth partition, read-only case progress for clients.

**Not included:** Secure messaging, document upload from portal, billing, mobile apps.

### AI Assistance — LLM (Partial)

**Included:** Provider configuration, PII policy ADR, opt-in LLM summaries behind `ENABLE_LLM`.

**Not included:** Autonomous agents, external PII export without explicit org config.

## Related documents

- [Version 4.8 completion checklist](../development/version-4.8-completion-checklist.md)
- [Capability matrix](capability-matrix.md)
- [Product roadmap](../roadmap/README.md)
- [Version 4.5 scope](version-4.5-scope.md)
