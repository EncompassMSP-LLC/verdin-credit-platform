# Loan Officer Database

**Lending Readiness Partners**

Contact-level record. Always linked to a Mortgage Company org.

## Fields

| Field                   | Type      | Required    | Notes                                          |
| ----------------------- | --------- | ----------- | ---------------------------------------------- |
| contact_id              | ID        | Yes         |                                                |
| org_id                  | ID        | Yes         | Parent mortgage company                        |
| first_name              | Text      | Yes         |                                                |
| last_name               | Text      | Yes         |                                                |
| nmls_id                 | Text      | Recommended |                                                |
| email                   | Email     | Yes         |                                                |
| mobile                  | Phone     | No          | TCPA consent before SMS                        |
| role_title              | Text      | No          | LO, producer, branch mgr                       |
| platform_partner_role   | Enum      | No          | e.g. `loan_officer`, `lender_admin`            |
| branch_location         | Text      | No          |                                                |
| preferred_channel       | Enum      | No          | email · phone · text · portal                  |
| status                  | Enum      | Yes         | Prospect · Active · Nurture · Paused · Churned |
| quick_start_sent        | Bool      | No          |                                                |
| quick_start_ack_date    | Date      | No          |                                                |
| referrals_30d           | Number    | Calc        |                                                |
| referrals_90d           | Number    | Calc        |                                                |
| last_referral_date      | Date      | No          |                                                |
| last_touch_date         | Date      | No          |                                                |
| next_action             | Text      | No          |                                                |
| relationship_score      | 1–5       | No          |                                                |
| owner_rep               | Text      | Yes         | Usually inherits org owner                     |
| notes                   | Long text | No          |                                                |
| created_at / updated_at | Timestamp | Yes         |                                                |

## CSV header

```csv
contact_id,org_id,first_name,last_name,nmls_id,email,mobile,role_title,branch_location,preferred_channel,status,quick_start_sent,last_referral_date,last_touch_date,next_action,relationship_score,owner_rep,notes
```

## Rules

- Do not create orphan LOs without an org.
- When LO changes companies, close/reassign old link; create new contact-org link (keep history).
