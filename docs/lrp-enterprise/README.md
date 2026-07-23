# Lending Readiness Partners — Enterprise Workspace

Cursor-facing organization for the **LRP enterprise edition** inside the Ultimate Credit Repair / Verdin monorepo.

**Program mode:** Blueprint-first — see the **[Enterprise Build Bible v2.0](build-bible/README.md)** and **[five stages](stages/README.md)**. Spec before screen; screen before code.

**Rule:** This is an **edition packaging layer**, not a forked product. Runtime code stays in shared `apps/` and `packages/`. Use this tree for docs, assets, and agent navigation.

| Ideal mental model (`/lrp-enterprise/`) | Actual monorepo location                                    |
| --------------------------------------- | ----------------------------------------------------------- |
| `docs/*`                                | [`docs/lrp-enterprise/`](.) (this tree)                     |
| `apps/website`                          | [`apps/lrp-web`](../../apps/lrp-web) marketing routes       |
| `apps/borrower-portal`                  | `apps/lrp-web` → `/portal` + portal APIs                    |
| `apps/lender-portal`                    | `apps/lrp-web` → `/lender` + mortgage partner APIs          |
| `apps/admin`                            | [`apps/web`](../../apps/web) (CRO staff) + org-admin APIs   |
| `apps/crm`                              | `apps/lrp-web` → `/crm`                                     |
| `packages/*`                            | Shared [`packages/`](../../packages) + platform API modules |
| `assets/*`                              | [`assets/lrp/`](../../assets/lrp)                           |

**Canonical architecture:** [../architecture/lending-readiness-partners.md](../architecture/lending-readiness-partners.md) (when present) · [Version 29.0 scope](../governance/version-29.0-scope.md)  
**Structure map:** [STRUCTURE.md](STRUCTURE.md)

---

## Docs index

| #   | Folder                                 | Focus                              |
| --- | -------------------------------------- | ---------------------------------- |
| 00  | [Executive](00-executive/)             | Vision, KPIs, edition strategy     |
| 01  | [Brand](01-brand/)                     | Identity, voice, visual system     |
| 02  | [Marketing](02-marketing/)             | Campaigns, content, channels       |
| 03  | [Sales](03-sales/)                     | Partner kits, pricing, playbooks   |
| 04  | [Operations](04-operations/)           | Runbooks, SLAs, staffing           |
| 05  | [Website](05-website/)                 | Marketing site IA & copy           |
| 06  | [Borrower Portal](06-borrower-portal/) | Consumer experience                |
| 07  | [Lender Portal](07-lender-portal/)     | Partner workspace                  |
| 08  | [AI](08-ai/)                           | Credit analysis, ADR-012 gates     |
| 09  | [CRM](09-crm/)                         | Operator CRM                       |
| 10  | [API](10-api/)                         | Partner & platform APIs            |
| 11  | [Legal](11-legal/)                     | Contracts, trademarks, disclaimers |
| 12  | [Compliance](12-compliance/)           | FCRA, SOC2-ready controls          |
| 13  | [SOPs](13-sops/)                       | Standard operating procedures      |
| 14  | [Training](14-training/)               | Enablement curricula               |
| 15  | [Roadmap](15-roadmap/)                 | Phases & release tracking          |
