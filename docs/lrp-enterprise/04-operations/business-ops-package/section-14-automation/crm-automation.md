# CRM Task Automation

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

Aligns with Section 5 CRM lifecycle and `/crm` workspace.

---

## 1. Auto-created activities / tasks

| Trigger                              | Task                                                | Owner                | Due            |
| ------------------------------------ | --------------------------------------------------- | -------------------- | -------------- |
| Website B2B contact                  | Qualify lead + send kit                             | Partner Success      | Same day       |
| Referral submitted                   | Assign case manager + CS notify                     | Ops rules            | Immediate      |
| Consultation completed               | Generate readiness pack (advisory) + partner notify | Credit Specialist    | 1 business day |
| Partner no activity 14d              | Touch / health check                                | Relationship owner   | 2 days         |
| Partner health below 65              | Attention plan                                      | Partner Success lead | 3 days         |
| Agreement sent                       | Follow up for signature                             | Partner Success      | 3 days         |
| Training incomplete 7d after onboard | Nudge LO Quick Start                                | Partner Success      | 2 days         |
| Overdue referral ack SLA             | Escalate                                            | Partner Success lead | Immediate      |

---

## 2. Lifecycle stage automation

| Stage enter       | Automations                                           |
| ----------------- | ----------------------------------------------------- |
| Prospect          | Enroll Day 1/3/7/14/21/30 nurture (Section 5 cadence) |
| First Outreach    | Create call task                                      |
| Discovery Meeting | Calendar hold + prep checklist                        |
| Qualified         | Create agreement task                                 |
| Onboarding        | Send Welcome Guide + training links                   |
| Active Partner    | Weekly status task template enabled                   |
| Referral Received | Pipeline record + notifications (Section 4)           |
| Churned / Paused  | Stop sequences; retain audit                          |

---

## 3. Deduplication hooks

On create/import:

1. Match org by normalized name + domain
2. Match contact by email
3. If duplicate → merge suggestion task (human confirm) — never silent destructive merge

---

## 4. Daily workflow digest (CRM home)

Scheduled job builds command-center queue:

1. Overdue tasks
2. Today’s meetings
3. Today’s calls
4. Today’s follow-ups
5. Referral notifications
6. Partner messages
7. Daily KPI snapshot

Surface in `/crm` dashboard (product) + optional morning email to Partner Success.

---

## 5. Audit

Every auto-task writes CRM activity with `source=automation`, `rule_key`, `trigger_event_id`.
