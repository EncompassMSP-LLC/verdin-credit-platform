# Referral Intake Automation

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

Maps Section 4 referral tracker + Section 12 referral form to platform events.

---

## 1. On referral submit (atomic checklist)

When a partner (e.g. realtor/LO) submits a referral:

| Step | Automation                                           | System                                |
| ---- | ---------------------------------------------------- | ------------------------------------- |
| 1    | Thank-you email to referrer                          | notifications                         |
| 2    | Thank-you / expectations email to borrower           | notifications                         |
| 3    | Assign Case Manager (round-robin or territory rules) | CRM / cases                           |
| 4    | Notify Credit Specialist                             | notifications + CRM task              |
| 5    | Offer/schedule consultation (link or task)           | appointments                          |
| 6    | Create CRM activity                                  | CRM                                   |
| 7    | Create pipeline / loan milestone record              | `mortgage_partner` / Section 4 stages |
| 8    | Notify Loan Officer                                  | notifications                         |
| 9    | Ack SLA timer start                                  | ops metrics                           |

All claim-safe; no auto-filing of disputes.

---

## 2. Field validation (before accept)

- Required: borrower name, phone or email, referring partner, product intent
- Reject/quarantine: SSN pasted in free-text; full report dumps
- Duplicate suspect: same phone/email open referral → merge review task

---

## 3. Consultation completed pack

When consultation marked complete, generate **draft** artifacts for staff review:

| Artifact                          | Notes                                             |
| --------------------------------- | ------------------------------------------------- |
| Advisory Readiness Score snapshot | Disclaimer required                               |
| Timeline (illustrative)           | Not a guarantee                                   |
| Action plan / tasks               | Portal tasks                                      |
| Status report stub                | Section 6/7 templates                             |
| Partner notification draft        | LO/realtor — send after review if policy requires |

---

## 4. Pipeline stage hooks

On stage change (ops overlay ↔ `LoanPipelineStage`):

- Notify authorized partners on meaningful transitions
- Create tasks for missing docs at Documentation stage
- On advisory Mortgage Ready: notify LO; never auto-submit to lender LOS

---

## 5. Failure handling

| Failure                | Behavior                                      |
| ---------------------- | --------------------------------------------- |
| Notify send fail       | Retry with backoff; escalate after N          |
| Assignment rules empty | Task to ops lead: “Unassigned referral”       |
| Partial write          | Compensate / mark referral `needs_ops_review` |
