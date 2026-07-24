# Attorney Database

**Lending Readiness Partners**

Ops subtype: `attorney` · Platform: `PartnerOrgType.other`

Typical use: foreclosure / consumer / real-estate counsel who encounter clients needing mortgage-readiness education (not legal advice from LRP).

## Fields

| Field              | Type      | Required | Notes                          |
| ------------------ | --------- | -------- | ------------------------------ |
| org_id / firm_name | ID / Text | Yes      |                                |
| contact_name       | Text      | Yes      |                                |
| practice_areas     | List      | No       | e.g. real estate, consumer     |
| bar_state          | Text      | No       |                                |
| email / phone      |           | Yes / No |                                |
| partnership_status | Enum      | Yes      |                                |
| referral_direction | Enum      | No       | `to_lrp` · `from_lrp` · `both` |
| conflict_notes     | Text      | No       | High-level only                |
| owner_rep          | Text      | Yes      |                                |
| last_touch_date    | Date      | No       |                                |
| notes              | Long text | No       | No privileged client detail    |

## Rules

- LRP does not provide legal services.
- Do not store privileged attorney-client content in CRM.
- Co-marketing requires mutual approval (see Partner Agreement).

## CSV header

```csv
org_id,firm_name,contact_name,practice_areas,bar_state,email,phone,partnership_status,referral_direction,owner_rep,last_touch_date,notes
```
