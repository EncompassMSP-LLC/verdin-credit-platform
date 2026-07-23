# Volume crosswalk — DOCX v2.0 ↔ repo Build Bible

| Field        | Value                                                                                                                                      |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| Status       | `ready-for-build`                                                                                                                          |
| Last updated | 2026-07-23                                                                                                                                 |
| Source DOCX  | [sources/Lending_Readiness_Partners_Enterprise_Build_Bible_v2.0.docx](sources/Lending_Readiness_Partners_Enterprise_Build_Bible_v2.0.docx) |

## Rule

- **Founder-facing outline:** DOCX 30-volume Enterprise Build Bible v2.0 (July 2026).
- **Build source of truth:** repo folders under `volumes/` (current ~25-volume scheme used by Stage 5 PRs).
- **Do not renumber** repo volumes mid–Stage 5. Cite **repo** vol numbers in PRs (`Vol 19`, `Vol 22`, …).
- When DOCX and repo diverge, absorb unique DOCX locks into the mapped repo volume (or CLAIM-LIBRARY) and note it here.

---

## DOCX → repo map

| DOCX # | DOCX title                                | Repo vol | Repo folder                               | Notes                                   |
| ------ | ----------------------------------------- | -------- | ----------------------------------------- | --------------------------------------- |
| 01     | Executive Charter and Strategic Thesis    | 01       | `01-vision-market`                        | Mission/vision/boundaries               |
| 02     | Brand Architecture and Messaging System   | 16 · CL  | `16-brand-protection` + CLAIM-LIBRARY     | Tagline, claims                         |
| 03     | Business Model and Revenue Architecture   | 02 · 04  | `02-business-plan` · `04-revenue-pricing` |                                         |
| 04     | Customer and Partner Personas             | 01 · 10  | vision + partner onboarding               |                                         |
| 05     | Service Catalog and Program Design        | 02 · 05  | business plan · organization              |                                         |
| 06     | Borrower Journey and Experience Blueprint | 11 · 19  | borrower onboarding · portal UX           |                                         |
| 07     | Lender Partner Program                    | 12 · 20  | lender onboarding · lender UX             |                                         |
| 08     | Realtor Partner Program                   | 13       | `13-realtor-onboarding`                   |                                         |
| 09     | Sales Playbook                            | 08       | `08-sales-playbook`                       |                                         |
| 10     | Marketing Strategy and Campaign System    | 07       | `07-marketing-launch`                     |                                         |
| 11     | Public Website Product Requirements       | — · 23   | `apps/lrp-web` marketing + design         | No dedicated vol yet; site in `lrp-web` |
| 12     | Borrower Portal Product Requirements      | 19       | `19-borrower-portal-ux`                   | Stage 5 E2                              |
| 13     | Partner Portal Product Requirements       | 20       | `20-lender-portal-ux`                     | “Partner” ≈ lender/realtor portal       |
| 14     | Internal CRM and Admin Console            | 21       | `21-crm-admin-ux`                         |                                         |
| 15     | AI Credit Analysis System                 | 22       | `22-ai-readiness-engine`                  | Stage 5 E3                              |
| 16     | Readiness Scoring Framework               | 22       | `22-ai-readiness-engine` + SCORE-MODEL    |                                         |
| 17     | Reporting and Document Generation         | 22 · 20  | engine + lender reports                   |                                         |
| 18     | Operations Manual                         | 14       | `14-sop-manual`                           |                                         |
| 19     | Standard Operating Procedures             | 14       | `14-sop-manual`                           |                                         |
| 20     | Customer Service and Communications       | 09       | `09-customer-service`                     |                                         |
| 21     | Compliance and Legal Guardrails           | 18       | `18-compliance`                           |                                         |
| 22     | Security, Privacy, and Data Governance    | 18 · 24  | compliance · technology                   |                                         |
| 23     | Technology Architecture                   | 24       | `24-technology-architecture`              | **Swapped vs DOCX 24**                  |
| 24     | Design System and Accessibility           | 23       | `23-design-system`                        | **Swapped vs DOCX 23**                  |
| 25     | Quality Assurance and Testing             | 25 · CI  | backlog + platform CI                     |                                         |
| 26     | Training and Certification                | 15       | `15-employee-handbook`                    |                                         |
| 27     | Financial Planning and KPI Framework      | 03 · 06  | financial model · KPIs                    |                                         |
| 28     | Launch and Go-to-Market Plan              | 07       | `07-marketing-launch`                     |                                         |
| 29     | Cursor Implementation System              | 25       | `25-implementation-backlog`               | Stage 5                                 |
| 30     | Canva Production System and Asset Library | 16 · —   | brand; assets stay out of git             | Large binaries not stored in monorepo   |

---

## Numbering note (DOCX vs repo)

| Topic            | DOCX  | Repo   |
| ---------------- | ----- | ------ |
| Design system    | 24    | **23** |
| Technology       | 23    | **24** |
| Cursor / backlog | 29    | **25** |
| Borrower portal  | 12    | **19** |
| Partner portal   | 13    | **20** |
| CRM              | 14    | **21** |
| AI + scoring     | 15–16 | **22** |

---

## Absorbed from DOCX (2026-07-23)

Unique non-scaffold locks from the DOCX were merged into:

- [CLAIM-LIBRARY.md](CLAIM-LIBRARY.md)
- [volumes/01-vision-market/README.md](volumes/01-vision-market/README.md)
- [volumes/22-ai-readiness-engine/README.md](volumes/22-ai-readiness-engine/README.md)
- [volumes/19-borrower-portal-ux/pages/dashboard.md](volumes/19-borrower-portal-ux/pages/dashboard.md)

DOCX sections that are still checklist-only remain scaffold; deepen those via Bible PRs when founders fill substance.
