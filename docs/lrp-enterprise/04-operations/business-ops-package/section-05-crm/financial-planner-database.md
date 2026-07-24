# Financial Planner Database

**Lending Readiness Partners**

Ops subtype: `financial_planner` · Platform: `other`

## Fields

| Field               | Type      | Required | Notes                            |
| ------------------- | --------- | -------- | -------------------------------- |
| org_id / firm_name  |           | Yes      |                                  |
| contact_name        | Text      | Yes      |                                  |
| credentials         | Text      | No       | CFP®, etc. (as provided)         |
| email / phone       |           | Yes / No |                                  |
| client_focus        | Text      | No       | e.g. first-time buyers, relocate |
| partnership_status  | Enum      | Yes      |                                  |
| owner_rep           | Text      | Yes      |                                  |
| last_touch_date     | Date      | No       |                                  |
| lunch_and_learn_fit | Bool      | No       |                                  |
| notes               | Long text | No       |                                  |

## Positioning

Planners refer clients prioritizing housing goals who need organized credit/documentation work before a lender conversation — advisory only.

## CSV header

```csv
org_id,firm_name,contact_name,credentials,email,phone,client_focus,partnership_status,lunch_and_learn_fit,owner_rep,last_touch_date,notes
```
