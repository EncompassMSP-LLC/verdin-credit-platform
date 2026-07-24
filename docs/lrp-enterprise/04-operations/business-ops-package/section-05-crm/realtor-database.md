# Realtor Database

**Lending Readiness Partners**

| Platform map | `PartnerOrgType.realtor` (org) + contacts |

## Organization fields (brokerage)

| Field                     | Type      | Required | Notes                            |
| ------------------------- | --------- | -------- | -------------------------------- |
| org_id                    | ID        | Yes      |                                  |
| brokerage_name            | Text      | Yes      |                                  |
| brokerage_license         | Text      | No       | State as applicable              |
| address / market_areas    | Text      | No       |                                  |
| website                   | URL       | No       |                                  |
| partnership_status        | Enum      | Yes      |                                  |
| owner_rep                 | Text      | Yes      |                                  |
| preferred_lender_partners | Text      | No       | Informal; no exclusivity assumed |
| last_touch_date           | Date      | No       |                                  |
| notes                     | Long text | No       |                                  |

## Agent (contact) fields

| Field            | Type      | Required | Notes                 |
| ---------------- | --------- | -------- | --------------------- |
| contact_id       | ID        | Yes      |                       |
| org_id           | ID        | Yes      | Brokerage             |
| name             | Text      | Yes      |                       |
| email / phone    |           | Yes / No |                       |
| license_number   | Text      | No       |                       |
| status           | Enum      | Yes      |                       |
| referrals_90d    | Number    | Calc     | Often via LO triangle |
| seminar_interest | Bool      | No       | Homebuyer seminar     |
| last_touch_date  | Date      | No       |                       |
| notes            | Long text | No       |                       |

## Positioning (claim-safe)

Realtors refer buyers who need readiness support before a strong lender conversation. LRP does not guarantee closings or approvals.

## CSV header (agents)

```csv
contact_id,org_id,name,email,phone,license_number,status,seminar_interest,last_touch_date,owner_rep,notes
```
