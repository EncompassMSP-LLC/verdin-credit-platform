# Verdin Credit Platform

> Version 4.2.0 — Platform Foundation

Production-grade credit operations platform featuring case management, document intelligence, automation, analytics, and AI-assisted workflows.

## Quick Start

```bash
# Install dependencies
pnpm install

# Configure environment
cp .env.example .env

# Start entire stack with Docker
docker compose up

# Run migrations and seed data
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed.py
```

### Access

| Service | URL |
|---------|-----|
| App (via Nginx) | http://localhost |
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| MinIO Console | http://localhost:9001 |

### Demo Login

| Email | Password | Role |
|-------|----------|------|
| owner@verdin.demo | changeme123 | Owner |
| admin@verdin.demo | changeme123 | Admin |

## Repository Structure

```
verdin-credit-platform/
├── apps/
│   ├── api/          # FastAPI backend
│   ├── web/          # React + Vite frontend
│   └── worker/       # Background job processor
├── packages/
│   ├── shared/       # Shared TypeScript types
│   ├── ui/           # Shared React components
│   └── validation/   # Shared Zod schemas
├── infrastructure/
│   ├── docker/
│   ├── nginx/
│   ├── postgres/
│   └── scripts/
├── docs/
├── tests/
├── .github/workflows/
├── .cursor/rules/
├── AGENTS.md
└── docker-compose.yml
```

## Development

```bash
# Run all apps in dev mode
pnpm dev

# Lint and typecheck
pnpm lint
pnpm typecheck

# Python tests
cd apps/api && pytest

# Format code
pnpm format
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, Vite, TypeScript, Tailwind, TanStack Query |
| Backend | FastAPI, Python 3.13, Pydantic v2, SQLAlchemy 2.x |
| Database | PostgreSQL 16, Alembic |
| Cache | Redis 7 |
| Storage | MinIO |
| Auth | JWT + Refresh Tokens, RBAC |
| Infra | Docker Compose, Nginx |
| CI/CD | GitHub Actions |
| Monorepo | pnpm workspaces, Turborepo |

## Documentation

- [Architecture](docs/architecture/overview.md)
- [Database ERD](docs/database/erd.md)
- [API Reference](docs/api/reference.md)
- [Authentication](docs/api/authentication.md)
- [Deployment](docs/deployment/guide.md)
- [Developer Guide](docs/developer-guide.md)
- [Coding Standards](docs/coding-standards.md)
- [Release Notes](docs/release-notes/v4.2.0.md)
- [AGENTS.md](AGENTS.md) — AI development instructions

## Roadmap

1. **Sprint 1** — Platform Foundation (current)
2. **Sprint 2** — Data Platform
3. **Sprint 3** — Import & OCR
4. **Sprint 4** — Analytics & AI
5. **v5.0** — Enterprise Edition

## License

MIT — see [LICENSE](LICENSE)
