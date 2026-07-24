# Title Company Database

**Lending Readiness Partners**

Ops subtype: `title_company` · Platform: `other`

Relationship for networking and occasional borrower education referrals — not title/escrow services by LRP.

## Fields

| Field                 | Type      | Required | Notes                                 |
| --------------------- | --------- | -------- | ------------------------------------- |
| org_id / company_name |           | Yes      |                                       |
| markets               | Text      | No       |                                       |
| contact_name          | Text      | Yes      | Business development / closer liaison |
| email / phone         |           | Yes / No |                                       |
| partnership_status    | Enum      | Yes      |                                       |
| owner_rep             | Text      | Yes      |                                       |
| last_touch_date       | Date      | No       |                                       |
| co_marketing_approved | Bool      | No       | Joint pieces need approval            |
| notes                 | Long text | No       |                                       |

## CSV header

```csv
org_id,company_name,markets,contact_name,email,phone,partnership_status,co_marketing_approved,owner_rep,last_touch_date,notes
```
