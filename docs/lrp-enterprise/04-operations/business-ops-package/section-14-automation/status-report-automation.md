# Status & Report Automation

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

Aligns with Section 6 status reports and Section 7 readiness reports.

---

## 1. Scheduled report jobs

| Job                        | Cadence   | Audience             | Output                        |
| -------------------------- | --------- | -------------------- | ----------------------------- |
| Weekly partner digest      | Weekly    | LO / broker (opt-in) | Section 6 weekly fields       |
| Monthly management pack    | Monthly   | Ops / exec           | Section 6 monthly             |
| Quarterly review pack      | Quarterly | Exec + top partners  | Section 6 quarterly           |
| Overdue investigation scan | Daily     | Staff                | Existing worker job pattern   |
| Reporting MV refresh       | Scheduled | Internal analytics   | `reporting_mv_refresh` worker |

---

## 2. Event-driven readiness reports

| Trigger               | Draft report       | Gate before send |
| --------------------- | ------------------ | ---------------- |
| Intake complete       | Initial assessment | Staff review     |
| ~30 days in program   | 30-day report      | Staff review     |
| ~60 days              | 60-day report      | Staff review     |
| Advisory ready / exit | Final report       | Staff review     |

Product may already expose mortgage readiness export (v29.0+); automation enqueues generation + notifies owner — **does not** auto-email partners until approved if org policy requires approval.

---

## 3. Distribution rules

| Recipient | Channel                  | Condition                   |
| --------- | ------------------------ | --------------------------- |
| Borrower  | Portal + email           | Report published            |
| LO        | Lender workspace + email | Authorization on file       |
| Realtor   | Email                    | Authorization + org setting |
| Internal  | CRM attach               | Always                      |

---

## 4. Content constraints

- Claim-library locked
- Advisory disclaimer on every readiness artifact
- No fabricated FICO before/after
- Composite examples only when used in marketing digests

---

## 5. Worker mapping

| Spec job         | Likely implementation                |
| ---------------- | ------------------------------------ |
| Digests          | New scheduled job + email templates  |
| MV refresh       | `apps/worker` `reporting_mv_refresh` |
| Overdue scans    | `overdue_investigation_scan`         |
| Readiness export | API export endpoints + notify        |
