# Builder Database

**Lending Readiness Partners**

Ops subtype: `builder` · Platform: `other`

New-construction partners whose buyers need readiness support before financing conversations.

## Fields

| Field                 | Type      | Required | Notes                       |
| --------------------- | --------- | -------- | --------------------------- |
| org_id / builder_name |           | Yes      |                             |
| markets               | Text      | No       | Cities / counties           |
| contact_name          | Text      | Yes      | Sales counselor / preferred |
| email / phone         |           | Yes / No |                             |
| preferred_lenders     | Text      | No       | Informational               |
| partnership_status    | Enum      | Yes      |                             |
| community_list        | Text      | No       | Active communities          |
| owner_rep             | Text      | Yes      |                             |
| last_touch_date       | Date      | No       |                             |
| notes                 | Long text | No       |                             |

## Claim-safe note

Do not promise buyers will qualify for builder incentives or preferred-lender programs.

## CSV header

```csv
org_id,builder_name,markets,contact_name,email,phone,preferred_lenders,partnership_status,community_list,owner_rep,last_touch_date,notes
```
