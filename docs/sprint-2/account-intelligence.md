# Sprint 2 Epic 2: Credit Account Intelligence Engine

**Date:** 2026-06-28

## Summary

Replaced the Sprint 1 client-account placeholder with a full credit tradeline module. Accounts are linked to cases via `case_id` and include bureau data, financial fields, dispute workflow, and computed intelligence scores.

## Backend

- Migration `003_credit_accounts` — drops legacy account columns and `cases.account_id`; creates credit tradeline schema with PostgreSQL enums
- Module: `api/modules/accounts/` — model, schemas, repository, service, router, permissions, intelligence scoring
- Endpoints under `/api/v1/accounts` plus `GET /api/v1/cases/{case_id}/accounts`
- RBAC: read = `read_only+`, write = `case_manager+`, delete = `admin+`
- Tests: `apps/api/tests/accounts/`

## Intelligence

`GET /api/v1/accounts/intelligence/summary` returns aggregates, breakdowns by bureau/type/status, highest balance/risk accounts, and a next-action queue.

Scoring heuristics in `intelligence.py`:

- **risk_score** — payment status, account status, past-due amount, balance
- **readiness_score** — dispute status, evidence completeness, investigation state, dispute cooldown
- **next_eligible_dispute_date** — 30 days after `last_dispute_date`
- **dispute_status** — auto-derived from evidence and cooldown unless in an active dispute state

## Frontend

- Accounts list with filters, intelligence summary cards, next-action queue
- Account detail, create/edit forms, delete confirmation
- Case-linked account view at `/cases/:caseId/accounts`

## Packages

- `@verdin/shared` — account enums and labels
- `@verdin/validation` — `createAccountSchema`, `updateAccountSchema`
- `@verdin/api-client` — `createAccount`, `listAccounts`, `getAccount`, `updateAccount`, `deleteAccount`, `listCaseAccounts`, `getAccountIntelligenceSummary`
