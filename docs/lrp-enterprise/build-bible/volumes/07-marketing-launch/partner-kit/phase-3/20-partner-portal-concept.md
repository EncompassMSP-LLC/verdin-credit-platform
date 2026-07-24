# 20 — Partner Portal Concept

| Field   | Value                                    |
| ------- | ---------------------------------------- |
| Status  | `ready-for-build` (concept)              |
| Extends | Phase 2 `19-partner-portal-onboarding`   |
| Product | Aligns with Version 29.0 lender surfaces |

UI concept for lender/realtor partners. Implementation ships via product track—not marketing-only.

---

## Capabilities

| Module                | Description                                                                                |
| --------------------- | ------------------------------------------------------------------------------------------ |
| Referral dashboard    | Submit / track referrals by stage                                                          |
| Client status updates | Scoped stages: referred → in plan → progressing → lending-ready signal → returned / closed |
| Document uploads      | Partner-safe uploads where permitted; prefer borrower portal for PII-heavy docs            |
| Progress reports      | Weekly digest archive + on-demand summary                                                  |
| Secure messaging      | Threaded, audited messages (no SMS-of-record for sensitive data)                           |
| Marketing downloads   | Digital partner kit library                                                                |

---

## Stages (pipeline)

`referred` → `intake` → `in_repair_plan` → `mortgage_ready_advisory` → `in_underwriting` (partner-marked) → `funded_or_declined` (partner-marked)

Advisory “mortgage ready” ≠ approval.

---

## Permissions

| Role             | Access                        |
| ---------------- | ----------------------------- |
| Partner admin    | Seats, kit, all org referrals |
| Loan officer     | Own referrals + digests       |
| Realtor (scoped) | Own referrals; limited fields |
| CRO staff        | Full ops                      |

---

## Explicit non-goals

- Cross-tenant marketplace
- Live bureau soft-pull for partners
- Unsupervised filing controls
- Replacing LOS underwriting

---

## Wireframe notes

1. Login → dashboard KPIs (counts only)
2. Referral table + filters
3. Referral detail: timeline, tasks complete %, last update
4. Resources tab → kit downloads
5. Message composer with disclaimer reminder

See product APIs under `apps/api/api/modules/mortgage_partner/`.
