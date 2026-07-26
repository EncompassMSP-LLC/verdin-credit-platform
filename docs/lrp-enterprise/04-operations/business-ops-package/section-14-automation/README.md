# Section 14 — Automation

**Lending Readiness Partners** · Helping More Borrowers Become Lending Ready.

Operational automation specifications mapped to the shared platform (`apps/api`, `apps/worker`, `apps/lrp-web`). Automations notify, schedule, and assemble — they do **not** file disputes unsupervised or promise loan outcomes.

| Document                       | File                                                         |
| ------------------------------ | ------------------------------------------------------------ |
| Automation principles & gates  | [`00-automation-principles.md`](00-automation-principles.md) |
| Notification matrix            | [`notification-matrix.md`](notification-matrix.md)           |
| Email sequences                | [`email-automation.md`](email-automation.md)                 |
| CRM task automation            | [`crm-automation.md`](crm-automation.md)                     |
| SMS automation                 | [`sms-automation.md`](sms-automation.md)                     |
| Appointments / calendar        | [`appointment-automation.md`](appointment-automation.md)     |
| Referral intake automation     | [`referral-automation.md`](referral-automation.md)           |
| Status & report jobs           | [`status-report-automation.md`](status-report-automation.md) |
| Document pipeline hooks        | [`document-automation.md`](document-automation.md)           |
| AI chatbot (gated)             | [`ai-chatbot.md`](ai-chatbot.md)                             |
| Client / partner portal events | [`portal-automation.md`](portal-automation.md)               |
| Platform job map               | [`platform-job-map.md`](platform-job-map.md)                 |

## Hard deferrals

- Live unsupervised bureau filing / polling execution
- Automated re-dispute filing without staff gate
- Cross-tenant marketplace automation
- Any LLM action that invents legal conclusions or fabricates evidence (ADR-012)

## Related

- Section 4 referral tracker · Section 5 CRM · Section 6 status reports · Section 12 forms
- Modules: `notifications`, `documents`, `accounts`, `mortgage_partner`, `llm`
- Worker: `apps/worker` job registry

_Lending Readiness Score™ is advisory and not a loan approval or underwriting decision._
