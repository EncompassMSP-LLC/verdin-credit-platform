# Loan Officer Dashboard (spec)

**Lending Readiness Partners**

| Field     | Value                                                     |
| --------- | --------------------------------------------------------- |
| UI        | Partner portal — LO-scoped view                           |
| API seeds | pipeline list filtered by referring LO; dashboard-summary |

## Widgets

| Widget            | Content                                        |
| ----------------- | ---------------------------------------------- |
| My open referrals | Count + list                                   |
| Needs action      | Docs outstanding, silent >7d, questions for LO |
| Stage board       | Mini kanban by platform stage                  |
| Recent updates    | Last 10 stage/milestone changes                |
| Ready for you     | `mortgage_ready` hand-backs                    |

## Empty / compliance

- Empty: CTA to submit referral + Quick Start link
- Footer disclaimer: advisory readiness; not underwriting

## Permissions

LO sees only their referrals (or branch scope if lender_admin configures).
