# Lending Readiness Partners — Enterprise Build Bible v2.0

**Status:** P0–P2 **accepted** ([FOUNDER-REVIEW.md](./FOUNDER-REVIEW.md)). Stage 5 **E0–E3 shipped**; continue from Vol 25 backlog. Canonical: [STAGE-MODEL.md](./STAGE-MODEL.md) · [CLAIM-LIBRARY.md](./CLAIM-LIBRARY.md).  
**Purpose:** The operating manual that turns Cursor from a _design_ tool into an _implementation_ tool.  
**Product identity:** AI-powered **Borrower Readiness Platform** — not “another credit repair shop.”  
**Founder DOCX:** [sources/](./sources/) · map to repo vols via [VOLUME-CROSSWALK.md](./VOLUME-CROSSWALK.md) (do not renumber mid–Stage 5).

> **Working rule:** Spec before screen. Screen before code. No major product UI/API work until the relevant volume is marked **Ready for build**. Cite **repo** volume numbers in PRs.

---

## Why this exists

Coding LRP surfaces without a company + product blueprint produces rework as the business evolves. Fintech/SaaS companies that scale usually lock:

1. How the company operates (Stage 1)
2. What every screen does (Stage 2)
3. How it looks/behaves (Stage 3)
4. How it is built and run (Stage 4)
5. Then implementation (Stage 5)

This Bible is the single source of truth for all five stages.

---

## Five-stage program

| Stage | Name                                                               | Duration (guide) | Gate to exit                                                            |
| ----- | ------------------------------------------------------------------ | ---------------- | ----------------------------------------------------------------------- |
| **1** | [Company Blueprint](../stages/01-company-blueprint.md)             | 2–3 weeks        | Business operates on paper: plan, finance, SOPs, playbooks, org, KPIs   |
| **2** | [Product Blueprint](../stages/02-product-blueprint.md)             | 4–6 weeks        | Every portal/CRM screen: fields, buttons, workflows, empty/error states |
| **3** | [Design System](../stages/03-design-system.md)                     | 2–3 weeks        | Tokens, components, a11y, motion — approved                             |
| **4** | [Technology Architecture](../stages/04-technology-architecture.md) | 2–3 weeks        | Stack, security, DR, tenancy, AI gates — ADR-signed                     |
| **5** | [Cursor Development](../stages/05-cursor-development.md)           | Ongoing          | Build only from Ready volumes; PR = spec citation                       |

Detail: [stages/README.md](../stages/README.md)

---

## Product north star (locked intent)

```text
Upload 3 credit reports
        ↓
AI / engines read everything
        ↓
Issue detection (tradelines, inquiries, public records, …)
        ↓
Metro 2 review
        ↓
FCRA review
        ↓
Identity-theft indicators
        ↓
Lending Readiness Score™ (advisory)
        ↓
Personalized action plan
        ↓
Partner dashboard  ↔  Borrower dashboard
        ↓
Education modules + monthly progress
        ↓
Lender receives updates
        ↓
Borrower becomes Lending Ready
```

**Non-claims:** Not an underwriting decision. Not a funding guarantee. Disputes remain staff-mediated. No unsupervised bureau filing.

---

## Volume library (~25 volumes)

| Vol | Title                                   | Stage                | Folder                                                                    |
| --- | --------------------------------------- | -------------------- | ------------------------------------------------------------------------- |
| 01  | Vision, mission, market                 | 1 · **draft**        | [volumes/01-vision-market](volumes/01-vision-market/)                     |
| 02  | Business plan                           | 1 · **draft**        | [volumes/02-business-plan](volumes/02-business-plan/)                     |
| 03  | Financial model (3y / 5y)               | 1 · **draft**        | [volumes/03-financial-model](volumes/03-financial-model/)                 |
| 04  | Revenue & pricing                       | 1 · **draft**        | [volumes/04-revenue-pricing](volumes/04-revenue-pricing/)                 |
| 05  | Organization & roles                    | 1 · **draft**        | [volumes/05-organization](volumes/05-organization/)                       |
| 06  | KPIs & dashboards (business)            | 1 · **draft**        | [volumes/06-kpis-dashboards](volumes/06-kpis-dashboards/)                 |
| 07  | Marketing strategy & launch             | 1 · **draft**        | [volumes/07-marketing-launch](volumes/07-marketing-launch/)               |
| 08  | Sales playbook                          | 1 · **draft**        | [volumes/08-sales-playbook](volumes/08-sales-playbook/)                   |
| 09  | Customer service playbook               | 1 · **draft**        | [volumes/09-customer-service](volumes/09-customer-service/)               |
| 10  | Partner onboarding                      | 1 · **draft**        | [volumes/10-partner-onboarding](volumes/10-partner-onboarding/)           |
| 11  | Borrower onboarding                     | 1 · **draft**        | [volumes/11-borrower-onboarding](volumes/11-borrower-onboarding/)         |
| 12  | Lender onboarding                       | 1 · **draft**        | [volumes/12-lender-onboarding](volumes/12-lender-onboarding/)             |
| 13  | Realtor onboarding                      | 1 · **draft**        | [volumes/13-realtor-onboarding](volumes/13-realtor-onboarding/)           |
| 14  | SOP manual                              | 1 · **draft**        | [volumes/14-sop-manual](volumes/14-sop-manual/)                           |
| 15  | Employee handbook                       | 1 · **draft**        | [volumes/15-employee-handbook](volumes/15-employee-handbook/)             |
| 16  | Brand & trademark protection            | 1 · **draft**        | [volumes/16-brand-protection](volumes/16-brand-protection/)               |
| 17  | Legal & entity setup                    | 1 · **draft**        | [volumes/17-legal-entity](volumes/17-legal-entity/)                       |
| 18  | Compliance & FCRA posture               | 1→4 · **review**     | [volumes/18-compliance](volumes/18-compliance/)                           |
| 19  | Borrower portal UX spec                 | 2 · **draft/review** | [volumes/19-borrower-portal-ux](volumes/19-borrower-portal-ux/)           |
| 20  | Lender portal UX spec                   | 2 · **draft/review** | [volumes/20-lender-portal-ux](volumes/20-lender-portal-ux/)               |
| 21  | CRM & admin UX spec                     | 2 · **draft/review** | [volumes/21-crm-admin-ux](volumes/21-crm-admin-ux/)                       |
| 22  | AI & readiness engine spec              | 2→4 · **review**     | [volumes/22-ai-readiness-engine](volumes/22-ai-readiness-engine/)         |
| 23  | Design system                           | 3 · **review**       | [volumes/23-design-system](volumes/23-design-system/)                     |
| 24  | Technology architecture                 | 4 · **review**       | [volumes/24-technology-architecture](volumes/24-technology-architecture/) |
| 25  | Implementation backlog & Cursor prompts | 5 · **draft**        | [volumes/25-implementation-backlog](volumes/25-implementation-backlog/)   |

Cross-links to the lighter taxonomy: [../README.md](../README.md) (`00`–`15` folders).

---

## Volume status legend

| Status            | Meaning                               |
| ----------------- | ------------------------------------- |
| `stub`            | Outline only                          |
| `draft`           | Content in progress                   |
| `review`          | Ready for founder / compliance review |
| `approved`        | Locked for Stage exit                 |
| `ready-for-build` | Cursor may implement from this volume |

---

## Monorepo relationship (important)

This Bible lives in **`docs/lrp-enterprise/build-bible/`** inside the Verdin / Ultimate Credit Repair monorepo.

| Concern             | Decision for Stage 4 (default)                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------ |
| Product edition     | LRP on **shared platform** — do not fork a second codebase                                       |
| System of record    | Existing FastAPI + PostgreSQL multi-tenant API (`apps/api`)                                      |
| LRP UX app          | `apps/lrp-web` (website, `/portal`, `/lender`, `/crm`)                                           |
| Greenfield Supabase | **Not the default** — evaluate only if an ADR explicitly supersedes shared-platform architecture |
| Existing code       | Treat as **prototype / reference**; Bible may require rework or freeze until Stage 5             |

See Volume 24 for the full architecture decision record path.

---

## How to use with Cursor

1. Open the volume for the feature.
2. Confirm status is `ready-for-build`.
3. Cite section IDs in the PR description (`Vol 19 § Dashboard · fields`).
4. Do not invent workflows not present in the Bible — open a Bible PR first.

Cursor rule: `.cursor/rules/lrp-blueprint-first.mdc`
