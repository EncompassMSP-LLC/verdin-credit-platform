# Volume 22 — AI and readiness engine specification

| Field        | Value                                |
| ------------ | ------------------------------------ |
| Status       | `ready-for-build`                    |
| Stage        | 2–4                                  |
| Owner        | Product + engineering                |
| Last updated | 2026-07-22                           |
| Depends on   | Vol 14 · Vol 18 · Vol 19–21          |
| Downstream   | Vol 24 ADRs · Stage 5 implementation |

---

## 1. Purpose

Specify the **Borrower Readiness Platform** engine end-to-end so Stage 5 implements a product with clear identity — not ad-hoc features.

## 2. Target pipeline

```text
Upload 3 credit reports
  → Parse / OCR
  → Tradeline + inquiry + public record extraction
  → Metro 2 review pack
  → FCRA review pack
  → Identity-theft indicators
  → Utilization / late / collections / charge-off / inquiry audits
  → Lending Readiness Score™ (advisory composite)
  → Mortgage readiness report + lender summary
  → Borrower action plan + dispute recommendations (staff-mediated)
  → Timeline + monthly progress
  → Partner dashboard updates
  → Education modules
```

## 3. Reference implementation (prototype)

May be keep / refactor / replace after this volume is `ready-for-build`:

- Platform accounts / documents / compliance modules
- `packages/report-parsers/`
- Any `credit_analysis` orchestration in API (if present on branch)
- LRP portal readiness / learning / checklist surfaces

---

## 4. Inputs

| Input                | Requirement                        | Quality gate                                          |
| -------------------- | ---------------------------------- | ----------------------------------------------------- |
| Credit reports       | PDF (and/or structured pull later) | Readable; identity match to borrower                  |
| Bureau coverage      | Prefer EQ + EX + TU                | Score may publish as **partial** if &lt;3 with banner |
| ID / supporting docs | Per checklist                      | Staff accept before evidence-weighted findings        |
| Consents             | Platform consents on file          | Block analysis enqueue if missing                     |

**File types (draft):** PDF primary; images via OCR path; reject executables.

---

## 5. Pipeline stages (detailed)

| Stage                    | Deterministic?           | LLM?                               | Human gate                     |
| ------------------------ | ------------------------ | ---------------------------------- | ------------------------------ |
| Ingest / store           | Yes                      | No                                 | —                              |
| Parse / OCR              | Yes (parsers)            | Optional assist for low-confidence | Re-parse enqueue               |
| Entity extraction        | Mostly rules             | Optional augment (ADR-012)         | Reviewer on material overrides |
| Metro 2 pack             | Rules / catalogs         | Optional explain text              | Review before borrower-facing  |
| FCRA pack                | Rules                    | Optional explain text              | Review                         |
| ID-theft indicators      | Rules + signals          | No auto-label fraud                | **Always** staff confirm       |
| Audits (util/lates/etc.) | Rules                    | Optional                           | Spot-check                     |
| Score compose            | Deterministic formula    | No                                 | Publish action                 |
| Action plan              | Rules map findings→tasks | Optional wording                   | Edit before assign             |
| Dispute recommendations  | Heuristic                | Draft assist only                  | **Approve before send**        |
| Partner summary          | Template                 | Optional polish                    | Partner-visible lint           |
| Education suggest        | Rules                    | No                                 | —                              |

All external LLM calls require org LLM policy / `require_llm_ready()` per platform ADR-012. **No PII to external models without explicit org config.**

---

## 6. Lending Readiness Score™

### 6.1 Nature

Advisory composite for **mortgage-intent packaging**. Not FICO, Vantage, or underwriting.

### 6.2 Dimensions (draft weights — calibrate later)

| Dimension                         | Intent                                | Weight (draft) |
| --------------------------------- | ------------------------------------- | -------------- |
| D1 Payment / derogs               | Lates, collections, charge-offs       | 25%            |
| D2 Utilization                    | Revolving util bands                  | 15%            |
| D3 Public records / severe        | Bankruptcies, judgments (as reported) | 15%            |
| D4 Inquiries / new credit         | Recent inquiry pressure               | 10%            |
| D5 Cross-bureau consistency       | Material discrepancies                | 10%            |
| D6 Identity / file integrity      | Mixed file / ID-theft flags           | 10%            |
| D7 Documentation completeness     | Checklist readiness                   | 10%            |
| D8 Dispute / remediation progress | Open plan completion                  | 5%             |

Weights are product-owned; changes require version bump.

### 6.3 Bands (draft)

| Band          | Guidance (borrower-safe)                        |
| ------------- | ----------------------------------------------- |
| Building      | Foundational work remaining                     |
| Progressing   | Active remediation; not package-ready           |
| Near ready    | Minor gaps; partner can plan timeline           |
| Lending Ready | Ops marks package-eligible (still not approval) |

Numeric 0–100: **staff-only in v1**. Borrower v1 is **band-only** (FOUNDER-REVIEW P0-1).

### 6.4 Versioning

Each publish stores: `score_version`, `formula_version`, `inputs_hash`, `as_of`, `publisher_user_id`.

### 6.5 Disclaimer (canonical)

> Lending Readiness Score™ is an advisory tool for organizing credit and documentation work toward a mortgage conversation. It is not a credit score from a consumer reporting agency, not an underwriting decision, and not a guarantee of loan approval or terms.

---

## 7. Output artifacts

| Artifact                 | Audience             | Format      | Gate                        |
| ------------------------ | -------------------- | ----------- | --------------------------- |
| Findings pack (internal) | Staff                | JSON + UI   | Review overrides            |
| Borrower score + drivers | Borrower             | UI          | Publish                     |
| Action plan tasks        | Borrower + staff     | UI          | Edit/assign                 |
| Partner status summary   | LO / realtor         | UI + digest | Partner-visible fields only |
| Readiness package        | Authorized LO        | PDF/export  | Operator export approve     |
| Dispute letter draft     | Staff → send channel | PDF/text    | Reviewer approve            |

Retention: follow Vol 17 counsel + platform policy.

---

## 8. Visibility matrix

| Data                 | Borrower          | LO       | Realtor    | Staff |
| -------------------- | ----------------- | -------- | ---------- | ----- |
| Band                 | Yes               | Yes      | Coarse yes | Yes   |
| Numeric score        | Optional          | Optional | No         | Yes   |
| Drivers (high level) | Yes               | Limited  | No         | Yes   |
| Full tradelines      | No (summary only) | No       | No         | Yes   |
| Dispute letter body  | No (status only)  | No       | No         | Yes   |
| ID-theft case notes  | No                | No       | No         | Yes   |

---

## 9. Audit / rerun

- Every analysis run: run_id, model/parser versions, timestamps, actor
- Rerun allowed on new reports or manual “re-analyze”
- Overrides require reason code
- Score republish creates new version; prior retained

---

## 10. Failure modes

| Failure               | UX / system behavior                              |
| --------------------- | ------------------------------------------------- |
| Parse failure         | Status `parse_failed`; staff re-upload / re-parse |
| Missing bureau        | Partial analysis; banner on score                 |
| Identity mismatch     | Block publish; staff resolve                      |
| LLM unavailable       | Fall back to deterministic-only path              |
| Conflicting overrides | Block publish until resolved                      |

---

## 11. Explicit non-automation list

- No unsupervised bureau filing or live pull-to-file loops
- No auto-send of dispute letters
- No auto-label of identity theft as confirmed fraud
- No guarantee language in generated copy
- No cross-tenant training on customer PII
- No LOS underwriting decisioning

---

## 12. APIs (logical — Stage 4 binds routes)

| Capability           | Verb  | Notes                         |
| -------------------- | ----- | ----------------------------- |
| Enqueue analysis     | POST  | Case-scoped                   |
| Get run / findings   | GET   | Staff                         |
| Override finding     | PATCH | Audited                       |
| Publish score        | POST  | Audited                       |
| Generate action plan | POST  | May be side effect of publish |
| Partner summary      | GET   | Field-filtered                |
| Export package       | POST  | Gated                         |

Exact paths in Vol 24 / OpenAPI when implemented.

---

## 13. Open decisions

- [x] Band-only vs numeric for borrower v1 → **band-only borrower; numeric staff** (P0-1)
- [ ] Calibration dataset / expert review process
- [x] Which findings are LLM-eligible on day one → **none; deterministic-only until org LLM policy** (P2-12)
- [ ] Package PDF layout owner (design Vol 23)
- [x] Canonical stages → [STAGE-MODEL.md](../../STAGE-MODEL.md) (P0-3)

## Approval

| Role        | Name | Date | Sign-off |
| ----------- | ---- | ---- | -------- |
| Product     |      |      | ☐        |
| Compliance  |      |      | ☐        |
| Engineering |      |      | ☐        |
