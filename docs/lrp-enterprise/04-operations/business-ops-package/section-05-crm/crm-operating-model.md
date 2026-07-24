# CRM Operating Model

**Lending Readiness Partners**  
_Helping More Borrowers Become Lending Ready._

| Field        | Value                                             |
| ------------ | ------------------------------------------------- |
| Audience     | Partner Success, sales, ops                       |
| UI (product) | `apps/lrp-web` `/crm/*`                           |
| APIs         | clients, tasks, notifications, `mortgage_partner` |

---

## 1. Purpose

One place to track **who refers**, **who we nurture**, and **relationship health** — separate from the borrower case file and the referral pipeline (Section 4).

## 2. Object hierarchy

```text
Organization (company)
  └── Contact (person: LO, realtor, attorney, …)
        └── Partnership (active agreement / portal access)
              └── Referrals (Section 4 tracker)
                    └── Borrower / case (platform)
```

## 3. Partner type taxonomy

| Ops database      | Platform `PartnerOrgType` | `partner_subtype` (ops)                                    |
| ----------------- | ------------------------- | ---------------------------------------------------------- |
| Mortgage Company  | `lender` or `broker`      | `mortgage_company` / `credit_union` / `bank` / `brokerage` |
| Loan Officer      | (contact under org)       | `loan_officer`                                             |
| Realtor           | `realtor`                 | `realtor`                                                  |
| Attorney          | `other`                   | `attorney`                                                 |
| Financial Planner | `other`                   | `financial_planner`                                        |
| Insurance Agent   | `other`                   | `insurance_agent`                                          |
| Builder           | `other`                   | `builder`                                                  |
| Title Company     | `other`                   | `title_company`                                            |

Do not invent parallel company records for the same legal entity — one org, many contacts.

## 4. Lifecycle statuses (organization / contact)

| Status      | Meaning                          |
| ----------- | -------------------------------- |
| Prospect    | Identified; not yet pitched      |
| Engaged     | Discovery / deck delivered       |
| Contracting | Agreement in review              |
| Active      | Signed + referring (or ready to) |
| Nurture     | Warm; low volume                 |
| Paused      | Temporary stop                   |
| Churned     | Ended relationship               |

Align partnership record with platform `PartnershipStatus`: `pending` · `active` · `paused` · `ended`.

## 5. Required hygiene rules

1. Every Active org has an owner (Partner Success rep).
2. Every referring LO is a Contact linked to an Org.
3. No SSN / full credit files in CRM notes.
4. Claim-library language in templates and sequences.
5. Weekly: update last-touch + next action on Active + Engaged.
6. Monthly: pipeline of Prospects reviewed; dead Prospects archived.

## 6. Relationship score (ops, advisory)

Simple 1–5 for prioritization (not shown to partners as a “grade”):

| Score | Signal                                       |
| ----- | -------------------------------------------- |
| 5     | Regular referrals + responsive + trained LOs |
| 4     | Steady referrals                             |
| 3     | Occasional; needs nurture                    |
| 2     | Signed but silent                            |
| 1     | At risk / complaints                         |

## 7. Cadence

| Cadence   | Action                                      |
| --------- | ------------------------------------------- |
| Weekly    | Touch Active orgs with open referrals       |
| Monthly   | Business review for top partners            |
| Quarterly | Portfolio cleanup + training refresh        |
| Ad hoc    | New LO at Active company → Quick Start send |

## 8. Privacy

CRM holds B2B contact data and high-level referral metrics. Client-level credit detail stays in the case/portal vault — link by Referral Number only.

## 9. Related

- Section 1 onboarding kit
- Section 4 referral tracker
- Section 6 status reports
- Section 9 sales scripts
- Section 14 automation

---

_Helping More Borrowers Become Lending Ready._
