# Technical Debt Register — LRP Platform

Known shortcuts and refactoring tasks. Pay down during related feature work or dedicated hardening slices.

| Field        | Value      |
| ------------ | ---------- |
| Last updated | 2026-07-26 |

**Severity:** S1 blocker · S2 high · S3 medium · S4 low

---

| ID     | Debt                                                                     | Severity | Area       | Mitigation / paydown                                           |
| ------ | ------------------------------------------------------------------------ | -------- | ---------- | -------------------------------------------------------------- |
| TD-001 | Dual auth modes (platform + local demo) in non-prod                      | S3       | Auth       | LRP-108 production kill-switch shipped; demo for local DX only |
| TD-002 | CRM partners/pipeline/automations driven by `lib/crm/data.ts` mocks      | S2       | CRM        | LRP-101, LRP-102, LRP-203                                      |
| TD-003 | Dual auth modes increase bug surface                                     | S3       | Auth       | Consolidate on platform JWT; demo only in explicit DEV         |
| TD-004 | Readiness UI inconsistent across portal vs lender                        | S3       | Readiness  | LRP-104, LRP-106, LRP-401 shared components                    |
| TD-005 | Automations page is display-only scaffold                                | S2       | Automation | LRP-203 persist rules                                          |
| TD-006 | Marketing landings vs authenticated portals not clearly separated in nav | S4       | UX         | IA pass in M4/M5                                               |
| TD-007 | Large demo datasets in client bundles                                    | S3       | Perf       | Code-split; strip from prod builds                             |
| TD-008 | Checklist/exit criteria still open on v29.0 governance row               | S3       | Docs       | Close capability matrix sign-off                               |
| TD-009 | E2E coverage thin for LRP happy paths                                    | S2       | QA         | LRP-503 smoke suite                                            |
| TD-010 | Section 14 jobs not yet in worker registry                               | S2       | Worker     | M3 automation slices                                           |

---

## Rules

1. New debt requires an ID, severity, and paydown slice or backlog link.
2. Do not add debt that violates claim-library or filing gates.
3. Review this register at the start of each milestone.
