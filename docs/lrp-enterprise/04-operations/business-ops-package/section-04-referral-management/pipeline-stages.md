# Pipeline Stages — Ops Overlay ↔ Platform

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

Stages describe **workflow**, not underwriting decisions.

---

## Ops vocabulary (Business Ops Package)

| Ops stage              | Meaning                                   |
| ---------------------- | ----------------------------------------- |
| New Referral           | Received; not yet scheduled               |
| Consultation Scheduled | Consult on calendar                       |
| Documents Received     | Intake docs substantially complete        |
| Audit Completed        | Advisory analysis / initial plan done     |
| Dispute Phase          | Staff-mediated dispute work active        |
| Debt Reduction         | Utilization / payoff coaching focus       |
| Monitoring             | Waiting on bureau/creditor / check-ins    |
| Mortgage Ready         | LRP hand-back criteria met                |
| Returned to Lender     | Partner actively running loan process     |
| Closed Loan            | Partner reports funded                    |
| Lost Opportunity       | Withdrawn, unresponsive, or declined path |

---

## Platform enum (`LoanPipelineStage`)

Canonical product values (do not invent parallel DB enums without migration):

| Platform value    | Typical meaning                                   |
| ----------------- | ------------------------------------------------- |
| `referred`        | New referral received                             |
| `intake`          | Consultation / documents in progress              |
| `in_repair`       | Active readiness work (disputes, debt plan, etc.) |
| `near_ready`      | Most blockers cleared; finishing items            |
| `mortgage_ready`  | Ready for partner loan process                    |
| `in_underwriting` | At lender / UW                                    |
| `funded`          | Closed loan                                       |
| `declined`        | Loan declined (partner-reported)                  |
| `withdrawn`       | Client or partner withdrew                        |

---

## Mapping table (ops → platform)

| Ops stage              | Maps to platform               | Notes                                  |
| ---------------------- | ------------------------------ | -------------------------------------- |
| New Referral           | `referred`                     | Default on create                      |
| Consultation Scheduled | `intake`                       |                                        |
| Documents Received     | `intake`                       | Milestone flag preferred over new enum |
| Audit Completed        | `intake` → edge of `in_repair` | Use milestone “audit complete”         |
| Dispute Phase          | `in_repair`                    | Sub-status in notes/milestones         |
| Debt Reduction         | `in_repair`                    | Sub-status in notes/milestones         |
| Monitoring             | `in_repair` or `near_ready`    | Judgment by advisor                    |
| Mortgage Ready         | `mortgage_ready`               |                                        |
| Returned to Lender     | `in_underwriting`              | When partner confirms file live        |
| Closed Loan            | `funded`                       |                                        |
| Lost Opportunity       | `withdrawn` or `declined`      | Choose based on reason                 |

### Sub-stages without new enums

Prefer **milestones** + notes for Dispute / Debt Reduction / Monitoring rather than expanding `LoanPipelineStage` for every ops label. Expand enums only when reporting needs hard filters.

---

## Stage entry / exit criteria (ops)

| Stage                  | Enter when                            | Exit when                           |
| ---------------------- | ------------------------------------- | ----------------------------------- |
| New Referral           | Form/portal submit                    | Consult scheduled or lost           |
| Consultation Scheduled | Calendar hold                         | Consult complete                    |
| Documents Received     | Checklist substantially complete      | Audit done                          |
| Audit Completed        | Initial assessment delivered          | Plan accepted / work starts         |
| Dispute Phase          | First dispute packet approved to send | Disputes paused or complete         |
| Debt Reduction         | Utilization/paydown plan primary      | Plan complete or pivot              |
| Monitoring             | Waiting on external response          | New action or ready                 |
| Mortgage Ready         | Hand-back checklist met               | Partner takes over                  |
| Returned to Lender     | Partner confirms active loan          | Funded / declined / back to LRP     |
| Closed Loan            | Partner confirms funding              | Terminal                            |
| Lost Opportunity       | No path forward                       | Terminal (re-open via new referral) |

---

## Status vs stage

| Status     | Use                      |
| ---------- | ------------------------ |
| Active     | Any non-terminal stage   |
| On hold    | Client pause; keep stage |
| Closed won | `funded`                 |
| Lost       | `withdrawn` / `declined` |

---

_Lending Readiness Score™ is advisory and not a loan approval or underwriting decision._
