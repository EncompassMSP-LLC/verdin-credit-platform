# 07 — Lender Portal

Partner workspace for LOs, ops, and underwriter-view roles.

## Code

| Layer        | Path                                         |
| ------------ | -------------------------------------------- |
| UI           | `apps/lrp-web/src/app/lender/`               |
| Partner APIs | `apps/api/api/modules/mortgage_partner/`     |
| Client       | `packages/api-client` → `mortgagePartner.ts` |

## Flag

`ENABLE_MORTGAGE_PARTNER=true`

## Notes

UI may use demo auth until partner JWT lands. Data must stay partnership-scoped — never cross-tenant.
