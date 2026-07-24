# Section 5 — CRM Package

Partner relationship databases for Lending Readiness Partners. Use as spreadsheet/CRM schemas today; map into `apps/lrp-web` `/crm/*` and `mortgage_partner` as productized.

| Document                   | File                                                             |
| -------------------------- | ---------------------------------------------------------------- |
| CRM operating model        | [`crm-operating-model.md`](crm-operating-model.md)               |
| Mortgage Company Database  | [`mortgage-company-database.md`](mortgage-company-database.md)   |
| Loan Officer Database      | [`loan-officer-database.md`](loan-officer-database.md)           |
| Realtor Database           | [`realtor-database.md`](realtor-database.md)                     |
| Attorney Database          | [`attorney-database.md`](attorney-database.md)                   |
| Financial Planner Database | [`financial-planner-database.md`](financial-planner-database.md) |
| Insurance Agent Database   | [`insurance-agent-database.md`](insurance-agent-database.md)     |
| Builder Database           | [`builder-database.md`](builder-database.md)                     |
| Title Company Database     | [`title-company-database.md`](title-company-database.md)         |

Platform note: `PartnerOrgType` today is `lender` · `realtor` · `broker` · `operator` · `other`. Affiliate types below use ops `partner_subtype` until product expands the enum.
