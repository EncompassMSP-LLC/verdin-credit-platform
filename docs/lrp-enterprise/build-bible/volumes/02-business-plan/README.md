# Volume 02 — Business plan

| Field        | Value                                                                 |
| ------------ | --------------------------------------------------------------------- |
| Status       | `draft`                                                               |
| Stage        | 1 — Company Blueprint                                                 |
| Owner        | Founder                                                               |
| Last updated | 2026-07-22                                                            |
| Target depth | Expand toward 100+ pages via appendices (financials, SOPs, playbooks) |
| Depends on   | Vol 01 Vision                                                         |

This volume is the **spine**. Detailed playbooks, SOPs, and financial workbooks live in sibling volumes and are summarized here.

---

## Executive summary

**Lending Readiness Partners (LRP)** is an AI-powered **Borrower Readiness Platform** packaged for credit operators, lenders, and realtors. It transforms tri-bureau credit data into advisory readiness scores, action plans, borrower education, and partner-visible pipelines — while keeping dispute execution staff-mediated on a shared credit-operations platform.

**Business model (summary):** B2B SaaS / partner packaging fees to operators and channel partners, plus optional per-borrower or per-referral commercial terms (finalized in Vol 04).

**Ask of this plan:** Align capital, hiring, compliance, and product sequencing so Stage 5 engineering implements a defined company — not a guessing game.

---

## 1. Company overview

| Item             | Draft                                                          |
| ---------------- | -------------------------------------------------------------- |
| Brand            | Lending Readiness Partners                                     |
| Product category | Borrower Readiness Platform (fintech / proptech-adjacent SaaS) |
| Platform posture | Edition on Ultimate Credit Repair / Verdin shared platform     |
| Legal entity     | TBD — Vol 17 (GA LLC or counsel-advised structure)             |
| HQ / beachhead   | TBD                                                            |
| Stage            | Company blueprint (pre–Stage 5 product freeze)                 |

### 1.1 Elevator pitch

We help more borrowers become lending ready — with AI-assisted credit analysis, an advisory Lending Readiness Score™, borrower education, and partner dashboards lenders and realtors can trust — without pretending to underwrite loans.

### 1.2 Problem / solution / why now

|              |                                                                                                   |
| ------------ | ------------------------------------------------------------------------------------------------- |
| **Problem**  | Mortgage timing fails on opaque credit status; partners chase updates; consumers get hype.        |
| **Solution** | Structured analysis → readiness score → plan → education → partner visibility.                    |
| **Why now**  | Mortgage friction + partner demand for signals + mature OCR/parse/compliance engines on-platform. |

---

## 2. Products and services

### 2.1 Core product modules

| Module                      | Buyer value                                                  |
| --------------------------- | ------------------------------------------------------------ |
| Tri-bureau analysis engine  | Findings: Metro 2, FCRA, ID-theft indicators, related audits |
| Lending Readiness Score™    | Advisory composite + bands + blockers                        |
| Action plan & timeline      | Prioritized next steps; monthly progress                     |
| Borrower portal             | Tasks, docs, learning, messages                              |
| Lender portal               | Referrals, pipeline, readiness exports                       |
| Operator CRM                | Partners, tasks, automations, reporting                      |
| Staff ops (shared platform) | Cases, disputes, documents — system of record                |

### 2.2 Service layer (human)

Even as software, LRP assumes **staff-mediated** credit operations for dispute filing and high-risk actions. Pricing may bundle software + ops capacity (Vol 04).

### 2.3 What we refuse to sell

Guaranteed approvals, unsupervised bureau filing, cross-tenant applicant marketplaces, “black box” scores without auditability.

---

## 3. Market analysis

_Narrative detail in Vol 01 §6. This section is the business-plan form._

### 3.1 Target markets

1. Credit service operators with mortgage-intent book
2. Mortgage lenders / LO teams needing readiness handoff
3. Realtor groups feeding purchase pipelines

### 3.2 Beachhead strategy

Pick **one** primary GTM motion for Year 1:

| Option                             | Pros                            | Cons                              |
| ---------------------------------- | ------------------------------- | --------------------------------- |
| A. Operator-led (sell to CRO/ops)  | Controls compliance; deep usage | Longer sales cycle                |
| B. Lender-led (design-partner LOs) | Clear ROI story                 | Needs strong ops behind the brand |
| C. Hybrid                          | Balanced                        | Focus risk                        |

**Founder decision:** ☐ A · ☐ B · ☐ C · Notes: ________

### 3.3 Competitive positioning

Position against categories (repair mills, consumer apps, LOS, generic CRO tools) per Vol 01 §6.4. Maintain **compliance-forward** messaging as brand differentiation.

---

## 4. Go-to-market

Detail in Vol 07. Summary:

| Phase           | Motion                                                           |
| --------------- | ---------------------------------------------------------------- |
| Design partners | 3–10 lenders/realtors + 1–3 operators                            |
| Proof           | Case studies: referral → near-ready cycles (no guarantee claims) |
| Scale           | Partner kits, webinars, association channels                     |

Sales methodology → Vol 08. Onboarding → Vol 10–13.

---

## 5. Operations model

| Function        | How it runs                                      |
| --------------- | ------------------------------------------------ |
| Credit ops      | Shared platform cases/tasks/docs; SOPs in Vol 14 |
| Partner success | QBRs, readiness digests, SLA in Vol 09 / Vol 14  |
| Compliance      | Vol 18; staff gates; access audits               |
| Support         | Customer service playbook Vol 09                 |
| Org             | Chart & roles Vol 05                             |

---

## 6. Organization and hiring (summary)

Year-0 / Year-1 skeleton (expand Vol 05):

| Seat                            | Priority                          |
| ------------------------------- | --------------------------------- |
| Founder / GM                    | Now                               |
| Compliance lead (fractional OK) | Early                             |
| Credit ops lead                 | With first partners               |
| Partner / LO success            | With first lenders                |
| Engineering (platform edition)  | Stage 5 / ongoing shared platform |
| Marketing                       | Post–Stage 1 messaging lock       |

---

## 7. Financial overview

Full model → **Vol 03**. Pricing → **Vol 04**.

Plan-level statements to produce:

- [ ] 3-year P&L
- [ ] 5-year P&L
- [ ] Cash flow
- [ ] Headcount plan
- [ ] Unit economics (per partner, per active borrower)
- [ ] Sensitivity (churn, cycle length, attach rate)

---

## 8. Technology posture

Default: **edition on shared Verdin / Ultimate Credit Repair platform** (Vol 24). Prototype UI may exist; Stage 5 implements from Bible specs. Supabase greenfield only via ADR.

---

## 9. Risk register

| Risk                          | Mitigation                           |
| ----------------------------- | ------------------------------------ |
| Guarantee / marketing claims  | Disclaimer library; sales training   |
| Compliance incident           | Staff gates; audits; counsel         |
| Partner concentration         | Multi-partner beachhead              |
| Platform dependency           | Edition contract + roadmap alignment |
| Rewrite from premature coding | Blueprint-first program (this Bible) |
| Brand conflict / TM           | Vol 16 search before spend           |

---

## 10. Milestones

| Milestone                                | Target                                   |
| ---------------------------------------- | ---------------------------------------- |
| Stage 1 Bible exit                       | Company operates on paper                |
| Stage 2 UX specs complete                | Every screen specified                   |
| Stage 3–4 design + architecture approved | Build-ready                              |
| Stage 5 v1 partner + borrower loops      | Design partners live                     |
| Brand protection basics                  | Domain, entity path, handles (Vol 16–17) |

---

## 11. Appendices (link-out)

| Appendix              | Volume |
| --------------------- | ------ |
| A. Financial model    | 03     |
| B. Pricing            | 04     |
| C. Org chart          | 05     |
| D. KPIs               | 06     |
| E. Marketing & launch | 07     |
| F. Sales playbook     | 08     |
| G. Service playbook   | 09     |
| H. Onboarding guides  | 10–13  |
| I. SOP manual         | 14     |
| J. Employee handbook  | 15     |
| K. Brand & legal      | 16–17  |
| L. Compliance         | 18     |

---

## 12. Expansion to 100+ pages

Grow this volume by:

1. Filling every ☐ decision with founder answers
2. Attaching researched market numbers (cite sources)
3. Embedding partner personas and sample deal economics
4. Adding launch timeline (week-by-week for 90 days)
5. Including sample contracts outlines (counsel-reviewed)

---

## Approval

| Role          | Name | Date | Sign-off |
| ------------- | ---- | ---- | -------- |
| Founder       |      |      | ☐        |
| Advisor / CPA |      |      | ☐        |
