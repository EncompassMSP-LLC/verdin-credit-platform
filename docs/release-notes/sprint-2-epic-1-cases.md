# Sprint 2 — Case Management (Epic 1)

## Added

### Backend (`apps/api`)

- Expanded `cases` domain module with full CRUD
- Alembic migration `002_expand_cases_module` — new fields, enums, indexes
- Endpoints under `/api/v1/cases` (auth required)
- RBAC: read (all roles), write (`case_manager+`), delete (`admin+`)
- Integration tests in `tests/cases/`

### Frontend (`apps/web`)

- Cases list with search, filters, pagination, sorting
- Case detail, create, and edit pages
- Delete confirmation dialog
- Status chips and priority badges

### Packages

- `@verdin/shared` — case status, stage, priority types and labels
- `@verdin/validation` — create/update case Zod schemas
- `@verdin/api-client` — `createCase`, `listCases`, `getCase`, `updateCase`, `deleteCase`

## Case fields

`id`, `organization_id`, `case_number`, `title`, `client_name`, `client_email`, `status`, `stage`, `priority`, `assigned_user_id`, `summary`, `notes`, `opened_at`, `closed_at`, audit timestamps.

## Demo logins (after seed)

- `manager@verdin.demo` — case manager (create/edit)
- `admin@verdin.demo` — admin (delete)
- `owner@verdin.demo` — owner (all operations)
