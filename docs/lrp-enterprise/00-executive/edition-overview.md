# LRP edition overview (executive)

Lending Readiness Partners is a **product edition** of the Ultimate Credit Repair / Verdin Credit Platform.

| Principle           | Meaning                                                                           |
| ------------------- | --------------------------------------------------------------------------------- |
| Shared platform     | One API, one Postgres multi-tenant model, one compliance posture                  |
| Packaging layer     | Brand, portals, CRM, partner kits — not a cloned codebase                         |
| Advisory product    | Readiness scores and exports support handoff; they are not underwriting decisions |
| Partner-scoped data | Lenders see referred applicants only                                              |

## Surfaces

1. **Website** — acquisition and education
2. **Borrower portal** — checklist, readiness, documents, learning
3. **Lender portal** — referrals, pipeline, readiness visibility
4. **CRM** — operator channel management
5. **Admin** — CRO staff system of record (`apps/web`)

See [STRUCTURE.md](../STRUCTURE.md) for path mapping.
