# Mortgage Company Database

**Lending Readiness Partners**

Org-level record for banks, credit unions, mortgage companies, and brokerages.

## Fields

| Field                    | Type      | Required | Notes                                                      |
| ------------------------ | --------- | -------- | ---------------------------------------------------------- |
| org_id                   | ID        | Yes      | Platform org UUID when linked                              |
| legal_name               | Text      | Yes      |                                                            |
| dba                      | Text      | No       |                                                            |
| partner_subtype          | Enum      | Yes      | `bank` · `credit_union` · `mortgage_company` · `brokerage` |
| platform_partner_type    | Enum      | Yes      | `lender` or `broker`                                       |
| nmls_company_id          | Text      | No       |                                                            |
| hq_address               | Text      | No       |                                                            |
| website                  | URL       | No       |                                                            |
| primary_phone            | Phone     | No       |                                                            |
| primary_email            | Email     | No       | Ops / partnerships inbox                                   |
| partnership_status       | Enum      | Yes      | Prospect → Churned (see operating model)                   |
| agreement_signed_date    | Date      | No       |                                                            |
| agreement_version        | Text      | No       |                                                            |
| portal_enabled           | Bool      | No       |                                                            |
| owner_rep                | Text      | Yes      | Partner Success owner                                      |
| relationship_score       | 1–5       | No       | Ops only                                                   |
| target_monthly_referrals | Number    | No       | Planning, not a contractual quota by default               |
| actual_referrals_30d     | Number    | Calc     | From tracker                                               |
| actual_referrals_90d     | Number    | Calc     |                                                            |
| last_touch_date          | Date      | No       |                                                            |
| next_action              | Text      | No       |                                                            |
| next_action_date         | Date      | No       |                                                            |
| training_completed       | Bool      | No       | Office training done                                       |
| notes                    | Long text | No       | No consumer PII                                            |
| tags                     | List      | No       | e.g. `community_bank`, `wholesale`                         |
| created_at / updated_at  | Timestamp | Yes      |                                                            |

## CSV header

```csv
org_id,legal_name,dba,partner_subtype,platform_partner_type,nmls_company_id,hq_address,website,primary_phone,primary_email,partnership_status,agreement_signed_date,portal_enabled,owner_rep,relationship_score,last_touch_date,next_action,next_action_date,training_completed,notes,tags
```
