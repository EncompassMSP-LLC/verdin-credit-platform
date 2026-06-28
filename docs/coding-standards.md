# Coding Standards

## General Principles

1. **Minimize scope** — focused changes only
2. **Match conventions** — follow existing patterns
3. **Self-documenting code** — comments for non-obvious logic only
4. **Test meaningful behavior** — not trivial assertions

## Python

- Type hints on all function signatures
- Async/await for all database operations
- Pydantic v2 models for request/response validation
- Repository pattern for data access
- Service pattern for business logic
- 100 character line limit (Ruff)

```python
# Good: layered architecture
@router.get("/cases/{case_id}")
async def get_case(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CaseResponse:
    service = CaseService(db)
    return await service.get_case(case_id, current_user)

# Bad: direct database access in router
@router.get("/cases/{case_id}")
async def get_case(case_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Case).where(Case.id == case_id))
    return result.scalar_one()
```

## TypeScript

- Strict mode, no `any`
- Functional components with hooks
- Zod schemas for form validation
- TanStack Query for server state
- Tailwind utility classes for styling

## Git

- Branch naming: `feature/`, `fix/`, `docs/`
- Commit format: `type: description` (e.g., `feat: add case list endpoint`)
- One logical change per commit
- PRs require passing CI

## File Naming

| Type             | Convention | Example              |
| ---------------- | ---------- | -------------------- |
| Python modules   | snake_case | `auth_service.py`    |
| React components | PascalCase | `LoginPage.tsx`      |
| TypeScript utils | camelCase  | `api.ts`             |
| Docs             | kebab-case | `developer-guide.md` |
