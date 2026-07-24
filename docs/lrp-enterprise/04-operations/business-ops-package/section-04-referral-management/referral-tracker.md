# Referral Tracker

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

| Field                     | Value                                             |
| ------------------------- | ------------------------------------------------- |
| Use                       | Spreadsheet / CRM / partner portal list view      |
| Source of truth (product) | `partner_referrals` + pipeline stage + milestones |

---

## Required columns

| Column              | Description                                                    |
| ------------------- | -------------------------------------------------------------- |
| Referral Number     | System ID (or temporary ops ID until portal assign)            |
| Loan Officer        | Referring LO name + NMLS                                       |
| Company             | Partner company                                                |
| Borrower            | Client legal name                                              |
| Referral Date       | Date submitted                                                 |
| Current Stage       | See [`pipeline-stages.md`](pipeline-stages.md)                 |
| Expected Completion | Target hand-back / next milestone date (estimate, not promise) |
| Notes               | Short operational note (no full SSN)                           |
| Status              | Active / On hold / Closed won (funded) / Lost                  |

## Optional columns

| Column                   | Description                  |
| ------------------------ | ---------------------------- |
| Co-borrower              | If joint                     |
| Mortgage goal            | Purchase / refi              |
| Partner share authorized | Yes / No                     |
| Last touch               | Last LRP or LO contact date  |
| Readiness report         | Link / date of latest export |
| Closed loan date         | If Partner reports funding   |

## Weekly hygiene

1. Every active row has a stage + owner
2. No row silent > 7 business days without a note
3. Lost opportunities marked (do not leave as “New”)
4. Export snapshot for monthly partner report

## Spreadsheet starter (CSV header)

```csv
referral_number,loan_officer,company,borrower,referral_date,current_stage,expected_completion,notes,status
```
