# Email Automation

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

| Field        | Value                                                                    |
| ------------ | ------------------------------------------------------------------------ |
| Platform     | `notifications` module + worker delivery                                 |
| Copy sources | Section 9 email templates · Section 10 banks (marketing) · claim library |

---

## 1. Transactional sequences

### A. Partner lead (website contact)

| Day | Email                                  | Goal          |
| --- | -------------------------------------- | ------------- |
| 0   | Thanks + digital kit link              | Ack           |
| 1   | LO Quick Start / partnership one-pager | Educate       |
| 3   | Book briefing CTA                      | Convert       |
| 7   | Case-study composite (labeled)         | Nurture       |
| 14  | Break-up / stay-in-touch               | Close or park |

Stop on: briefing booked, partner marked Active, or unsubscribe.

### B. Referral received (borrower + partner)

| Audience         | Trigger T+0      | Content                                         |
| ---------------- | ---------------- | ----------------------------------------------- |
| Borrower         | Referral created | Thank-you; what to expect; no approval promises |
| Referring LO     | Referral created | Ack + referral number + next SLA                |
| Realtor (if any) | Referral created | Ack + dignity language                          |

### C. Consultation follow-up

| T+  | Email                                      |
| --- | ------------------------------------------ |
| 0   | Summary: advisory plan available in portal |
| 2   | Document checklist reminder                |
| 7   | Task progress nudge                        |

### D. Active partner cadence

| Cadence   | Email                                     |
| --------- | ----------------------------------------- |
| Weekly    | Optional open-referral digest (LO opt-in) |
| Monthly   | Performance snapshot (Section 6 fields)   |
| Quarterly | Business review invite                    |

---

## 2. Template keys (suggested)

```text
email.partner.lead.thanks
email.partner.lead.kit
email.partner.lead.briefing
email.referral.borrower.thanks
email.referral.lo.ack
email.consultation.summary
email.partner.monthly.digest
email.borrower.task.reminder
email.borrower.report.ready
```

---

## 3. Implementation notes

- Prefer existing email delivery repositories under `notifications`.
- Marketing drips distinct from transactional (separate suppression lists).
- Merge fields: partner name, LO name, referral number, portal URL — never full SSN / raw credit file.
- A/B only on subject lines that remain claim-safe.
