# Insurance Agent Database

**Lending Readiness Partners**

Ops subtype: `insurance_agent` · Platform: `other`

Common for homeowners / life agents in the homebuying circle of influence.

## Fields

| Field                | Type      | Required | Notes                      |
| -------------------- | --------- | -------- | -------------------------- |
| org_id / agency_name |           | Yes      |                            |
| contact_name         | Text      | Yes      |                            |
| lines                | List      | No       | home · auto · life         |
| email / phone        |           | Yes / No |                            |
| partnership_status   | Enum      | Yes      |                            |
| owner_rep            | Text      | Yes      |                            |
| last_touch_date      | Date      | No       |                            |
| event_interest       | Bool      | No       | Networking / lunch & learn |
| notes                | Long text | No       |                            |

## CSV header

```csv
org_id,agency_name,contact_name,lines,email,phone,partnership_status,event_interest,owner_rep,last_touch_date,notes
```
