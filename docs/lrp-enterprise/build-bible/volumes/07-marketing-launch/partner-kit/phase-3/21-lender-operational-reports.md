# 21 — Lender Operational Report Specs

| Field   | Value                                  |
| ------- | -------------------------------------- |
| Status  | `ready-for-build`                      |
| Product | Version 29.0+ intelligence / reporting |

These differentiate LRP from generic credit-repair updates: structured, actionable, advisory—not underwriting.

Each report: purpose · audience · inputs · sections · disclaimer · deferrals.

---

## 1. Mortgage Readiness Report

**Purpose:** Snapshot of advisory readiness for a referred borrower.  
**Sections:** Score/band (advisory) · Key findings · Priority tasks · Docs status · Partner notes  
**Disclaimer:** long form  
**Not included:** Approval prediction

## 2. Credit Improvement Roadmap

**Purpose:** Ordered plan (30/60/90 day focus areas—not promises).  
**Sections:** Themes (utilization, collections, docs) · Owner · Status

## 3. Metro 2 Compliance Summary

**Purpose:** Educational summary of Metro2-oriented findings from existing engines.  
**Not included:** Legal certification that a furnisher “violated” Metro2

## 4. FCRA Audit Summary

**Purpose:** Staff-facing audit trail of FCRA-related findings / actions.  
**Not included:** Legal conclusions for litigation without counsel

## 5. Bureau Comparison Report

**Purpose:** Cross-bureau discrepancy view from existing comparison tools.  
**Audience:** Staff + authorized partners (scoped fields)

## 6. Timeline of Reporting Changes

**Purpose:** Chronology of material report changes observed in-platform.  
**Not included:** Live bureau polling execution (deferred)

## 7. Identity Theft Alert Review

**Purpose:** Checklist + documented anomalies for staff review.  
**Escalation:** Counsel / official freeze processes as needed

## 8. Rapid Rescore Checklist

**Purpose:** Prep checklist when partner requests rescore conversation.  
**Not included:** Guaranteed rescore outcomes

## 9. Loan Readiness Scorecard

**Purpose:** One-page scorecard for LO desks (advisory dimensions).  
**Dimensions examples:** Docs completeness · Derogatory plan · Utilization plan · Inquiry hygiene · Partner update freshness

## 10. Borrower Progress Dashboard

**Purpose:** Portal/UI read model—tasks complete, education modules, last activity.

## 11. Loan Officer Status Reports

**Purpose:** Scheduled digest: counts by stage, referrals needing attention, no unnecessary PII.

---

## Implementation mapping

| Report                | Likely module                     |
| --------------------- | --------------------------------- |
| Readiness / scorecard | `mortgage_partner` + intelligence |
| Bureau comparison     | `accounts/cross_bureau`           |
| Metro2 / FCRA         | compliance / findings             |
| Digests               | notifications + reporting         |

Live bureau pulls and automated filing remain deferred per Version 29.0 scope.
