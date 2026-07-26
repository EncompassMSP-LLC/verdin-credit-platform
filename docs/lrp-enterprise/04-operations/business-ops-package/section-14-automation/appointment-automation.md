# Appointment Automation

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

---

## 1. Triggers

| Trigger                | Automation                                             |
| ---------------------- | ------------------------------------------------------ |
| Consultation scheduled | Calendar invites (borrower + specialist + optional LO) |
| Reschedule             | Cancel old holds; send updates                         |
| No-show                | Task for specialist; borrower reschedule email         |
| Completed              | Kick consultation-completed pack (see referral + CRM)  |

---

## 2. Booking rules

- Default length: 30 or 45 minutes (org setting)
- Buffer: 10 minutes
- Intake packet link (Section 2) in confirmation
- Reminder: email T-24h; SMS T-24h/T-1h if consented
- Zoom/Meet link generated or pasted by ops — store on CRM activity

---

## 3. Confirmation copy (email)

> Your consultation with Lending Readiness Partners is scheduled for [when].  
> We’ll review education and next steps toward your next financing conversation.  
> This is not a loan approval or underwriting decision.

---

## 4. Platform mapping

| Need            | Target                                                  |
| --------------- | ------------------------------------------------------- |
| CRM calendar UI | `apps/lrp-web` `/crm/calendar`                          |
| Task creation   | CRM tasks API                                           |
| Notifications   | `notifications` module                                  |
| Future sync     | Google/Microsoft calendar — Phase 4+ optional connector |

---

## 5. Outcomes on complete

Automation checklist when status → Completed:

1. CRM activity `consultation_completed`
2. Enqueue advisory readiness pack generation (staff-reviewed before partner send if required)
3. Notify LO / realtor per matrix
4. Schedule first task-reminder email for borrower
