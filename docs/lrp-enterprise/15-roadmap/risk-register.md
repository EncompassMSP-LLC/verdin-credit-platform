# Risk Register — Lending Readiness Platform™

Security, compliance, and operational risks with mitigation plans.

| Field        | Value      |
| ------------ | ---------- |
| Last updated | 2026-07-26 |

**Likelihood / Impact:** L/M/H  
**Status:** Open · Mitigating · Accepted · Closed

---

| ID     | Risk                                                  | L   | I   | Status     | Mitigation                                      | Owner           |
| ------ | ----------------------------------------------------- | --- | --- | ---------- | ----------------------------------------------- | --------------- |
| RK-001 | Unauthorized partner sees another partner’s borrowers | M   | H   | Mitigating | Tenant + partner scoping tests; LRP-108 session | Eng / Security  |
| RK-002 | Demo auth left enabled in production                  | M   | H   | Mitigating | Env flag + LRP-108 + deploy checklist           | Eng / Ops       |
| RK-003 | Unsupervised bureau filing shipped by mistake         | L   | H   | Mitigating | ADR + sprint rules; no filing endpoints in V1.0 | Compliance      |
| RK-004 | Misleading marketing claims vs claim library          | M   | H   | Mitigating | §9 claim library; review landings in M5         | Product / Legal |
| RK-005 | PII in LLM prompts without policy                     | M   | H   | Mitigating | ADR-012 `require_llm_ready()`                   | Eng             |
| RK-006 | SMS/TCPA violations from automation                   | M   | H   | Mitigating | Consent fields; §14 + LRP-202                   | Ops / Legal     |
| RK-007 | PDF report contains wrong readiness data              | M   | M   | Open       | LRP-201 golden fixtures                         | Eng / QA        |
| RK-008 | Partner CRM data loss / no backup                     | L   | H   | Open       | LRP-504 backups + DR                            | Ops             |
| RK-009 | Scope creep into product fork                         | L   | H   | Mitigating | ADR-013; decline fork requests                  | Product         |
| RK-010 | UAT blocked by incomplete portals                     | M   | M   | Open       | Milestone DoD; backlog deferrals explicit       | Product         |

---

## Review cadence

- Re-score at each milestone exit.
- Escalate H-impact Open risks to Product Owner before production cutover.
