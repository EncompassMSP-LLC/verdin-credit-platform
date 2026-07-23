# Volume 03 — Financial model (3-year / 5-year)

| Field        | Value                            |
| ------------ | -------------------------------- |
| Status       | `draft`                          |
| Stage        | 1 — Company Blueprint            |
| Owner        | Founder + CPA                    |
| Last updated | 2026-07-22                       |
| Depends on   | Vol 02 · Vol 04 (pricing inputs) |

**Note:** Figures below are **frameworks and placeholders**, not audited forecasts. Replace `TBD` / bracketed values with founder-CPA assumptions before Stage 1 exit.

---

## 1. Model purpose

- Size capital need and runway
- Stress-test partner and borrower growth
- Align hiring to revenue
- Feed investor / lender conversations with transparent assumptions

## 2. Entity & accounting basis

| Item                | Value                                                   |
| ------------------- | ------------------------------------------------------- |
| Entity              | TBD (Vol 17)                                            |
| Fiscal year         | Calendar / other: ____                                  |
| Currency            | USD                                                     |
| Revenue recognition | SaaS subscription + optional services (define with CPA) |

---

## 3. Core assumptions (driver table)

### 3.1 Go-to-market drivers

| Driver                            | Y1  | Y2  | Y3  | Y4  | Y5  | Notes               |
| --------------------------------- | --- | --- | --- | --- | --- | ------------------- |
| Active operator customers         |     |     |     |     |     | Paying CRO/ops orgs |
| Active lender partner orgs        |     |     |     |     |     |                     |
| Active realtor partner orgs       |     |     |     |     |     |                     |
| New referrals / month (exit rate) |     |     |     |     |     |                     |
| Active borrowers (EOP)            |     |     |     |     |     |                     |
| Avg months in program             |     |     |     |     |     | Cycle length        |
| Partner logo churn (annual)       |     |     |     |     |     |                     |
| Borrower completion / drop-off %  |     |     |     |     |     |                     |

### 3.2 Pricing drivers (from Vol 04)

| SKU                         | Unit                | Price | Notes    |
| --------------------------- | ------------------- | ----- | -------- |
| Operator platform           | /org/mo             | TBD   |          |
| Lender seat / portal        | /seat/mo or /org/mo | TBD   |          |
| Per active borrower         | /mo                 | TBD   | Optional |
| Per readiness export pack   | /each               | TBD   | Optional |
| Implementation / onboarding | one-time            | TBD   |          |

### 3.3 Cost drivers

| Category                    | Y1 monthly | Notes                          |
| --------------------------- | ---------- | ------------------------------ |
| Payroll + burden            |            | See headcount plan             |
| Contractors / counsel / CPA |            |                                |
| Cloud / infra / SaaS tools  |            | Shared platform allocation TBD |
| Marketing & partner events  |            |                                |
| Insurance (E&O, cyber)      |            |                                |
| Bureau / data vendors       |            | If any — compliance gated      |
| Misc / contingency          |            | % of opex                      |

---

## 4. Unit economics (templates)

### 4.1 Per partner logo

| Metric           | Formula                      | Value |
| ---------------- | ---------------------------- | ----- |
| ARPA (monthly)   | Sum of SKUs attached         |       |
| Gross margin %   | (ARPA − COGS) / ARPA         |       |
| CAC              | Sales+marketing / new logos  |       |
| Payback (months) | CAC / (ARPA × GM%)           |       |
| Logo LTV         | ARPA × GM% × lifetime months |       |

### 4.2 Per active borrower (if priced)

| Metric                          | Formula | Value |
| ------------------------------- | ------- | ----- |
| Revenue / borrower / mo         |         |       |
| Direct ops cost / borrower / mo |         |       |
| Contribution margin             |         |       |

---

## 5. Three-year P&L skeleton

| Line                                | Y1  | Y2  | Y3  |
| ----------------------------------- | --- | --- | --- |
| Recurring SaaS revenue              |     |     |     |
| Services / onboarding revenue       |     |     |     |
| **Total revenue**                   |     |     |     |
| COGS (hosting, vendors, direct ops) |     |     |     |
| **Gross profit**                    |     |     |     |
| Sales & marketing                   |     |     |     |
| R&D / product (platform edition)    |     |     |     |
| G&A                                 |     |     |     |
| **EBITDA**                          |     |     |     |
| Capex / one-time                    |     |     |     |
| Net income (approx.)                |     |     |     |

## 6. Five-year extension

Repeat P&L columns for Y4–Y5 with explicit growth rates:

| Driver                    | Y3→Y4 | Y4→Y5 |
| ------------------------- | ----- | ----- |
| Revenue growth %          |       |       |
| Headcount growth %        |       |       |
| Marketing as % of revenue |       |       |

---

## 7. Cash flow & runway

| Item                                  | Amount |
| ------------------------------------- | ------ |
| Starting cash                         |        |
| Monthly burn (steady)                 |        |
| Monthly burn (peak launch)            |        |
| Runway (months)                       |        |
| Capital raise / owner inject (if any) |        |

Minimum cash policy: ____ months opex.

---

## 8. Headcount plan (link Vol 05)

| Role                  | Y1 FTE | Y2  | Y3  | Fully loaded $/yr |
| --------------------- | ------ | --- | --- | ----------------- |
| GM / Founder          | 1      |     |     |                   |
| Compliance (frac→FTE) |        |     |     |                   |
| Credit ops            |        |     |     |                   |
| Partner success       |        |     |     |                   |
| Engineering (shared)  |        |     |     |                   |
| Marketing             |        |     |     |                   |
| Admin / finance       |        |     |     |                   |

---

## 9. Scenarios

| Scenario | Description               | Use            |
| -------- | ------------------------- | -------------- |
| Base     | Design-partner path       | Planning       |
| Upside   | Faster logo attach        | Hiring ceiling |
| Downside | Slow sales + higher churn | Runway floor   |

Document one sensitivity: **±20% cycle length** impact on borrower revenue.

---

## 10. Workbook location

Recommended: store Excel/Google Sheet as  
`assets/lrp/presentations/LRP-Financial-Model-v0.xlsx` (or Drive link listed here).

Link: ________

---

## 11. Open decisions

- [ ] Confirm SKU set with Vol 04
- [ ] Confirm whether ops labor is COGS or opex
- [ ] Platform cost allocation method from Ultimate Credit Repair
- [ ] Tax / entity assumptions with CPA

## Approval

| Role    | Name | Date | Sign-off |
| ------- | ---- | ---- | -------- |
| Founder |      |      | ☐        |
| CPA     |      |      | ☐        |
