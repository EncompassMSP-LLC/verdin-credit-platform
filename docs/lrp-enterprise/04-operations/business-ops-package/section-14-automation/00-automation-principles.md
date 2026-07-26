# Automation Principles & Gates

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

---

## 1. Purpose

Automate **repeatable ops** so Partner Success, credit specialists, and partners spend time on judgment—not copy/paste. Every automation must be auditable, claim-safe, and cancelable.

---

## 2. Design rules

| Rule                         | Meaning                                                                 |
| ---------------------------- | ----------------------------------------------------------------------- |
| Human-in-the-loop for filing | Dispute letters: draft/review/approve/send only after staff gates       |
| Advisory outputs             | Readiness scores, timelines, action plans are advisory—not underwriting |
| Consent-aware                | Email/SMS respect communication authorization + TCPA                    |
| Tenant-scoped                | No cross-org data in jobs or digests                                    |
| Idempotent                   | Re-runs must not double-notify or duplicate CRM tasks                   |
| Observable                   | Structured logs + CRM activity rows for every significant fire          |
| Claim-library copy           | Templates use approved language only                                    |

---

## 3. Trigger types

| Type      | Examples                                                      |
| --------- | ------------------------------------------------------------- |
| Event     | Referral submitted, consultation completed, document uploaded |
| Schedule  | Daily overdue tasks, weekly partner digest, monthly reports   |
| Threshold | Relationship health drops below 65; SLA breach                |
| Manual    | “Send kit” button; operator enqueue                           |

---

## 4. Severity / stop conditions

| Condition              | Behavior                                        |
| ---------------------- | ----------------------------------------------- |
| Missing consent        | Skip channel; log reason; create follow-up task |
| Bounce / SMS opt-out   | Suppress channel; update CRM                    |
| Partner paused/churned | Halt nurture sequences                          |
| Case closed            | Halt borrower sequences                         |
| Compliance hold        | Halt dispute-adjacent automations               |

---

## 5. Ownership

| Layer               | Owner                             |
| ------------------- | --------------------------------- |
| Spec (this section) | Ops + product                     |
| Template copy       | Marketing (claim library)         |
| Job implementation  | Engineering (`apps/worker` / API) |
| Runtime monitoring  | Ops + eng on-call                 |

---

## 6. Related ADRs / gates

- ADR-012 LLM readiness — `require_llm_ready()` before external LLM
- Dispute lifecycle — draft → review → approved → sent
- No unsupervised bureau submission (deferred product work)
