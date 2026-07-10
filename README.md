# Ultimate Credit Repair LLC

> Version 4.3.1 — Operational Core

Production-grade credit operations platform featuring case management, document intelligence, automation, analytics, and AI-assisted workflows.

**Current stable:** `v4.3.1` — Operational Core completion (Mission Control). **Sprint 4.3.1** (Operational Core Stabilization) is the current engineering milestone before Version 4.5 automation.

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

| Service         | URL                        |
| --------------- | -------------------------- |
| App (via Nginx) | http://localhost           |
| Frontend        | http://localhost:3000      |
| API             | http://localhost:8000      |
| API Docs        | http://localhost:8000/docs |
| MinIO Console   | http://localhost:9001      |

### Demo Login

| Email             | Password    | Role  |
| ----------------- | ----------- | ----- |
| owner@verdin.demo | changeme123 | Owner |

### Staff guides

- [Dispute workflow (step-by-step)](docs/guides/dispute-workflow.md) — import reports, cross-bureau compare, prepare letters, mail-ready export
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

### Pre-commit Hooks

Install [pre-commit](https://pre-commit.com/) once per clone to run lint and format checks before each commit:

```bash
# Install pre-commit (Python 3.13+)
pip install pre-commit

# Install Node dependencies (required for ESLint and Prettier hooks)
pnpm install

# Install API Python dependencies (recommended for local mypy/ruff)
cd apps/api && pip install -r requirements.txt

# Register git hooks
pre-commit install
```

Run all hooks manually against the full repository:

```bash
pre-commit run --all-files
```

Hooks included:

| Hook          | Tool        | Scope                                                      |
| ------------- | ----------- | ---------------------------------------------------------- |
| `ruff`        | Ruff lint   | `apps/api`, `apps/worker`                                  |
| `ruff-format` | Ruff format | `apps/api`, `apps/worker`                                  |
| `mypy-api`    | mypy        | `apps/api`                                                 |
| `prettier`    | Prettier    | TypeScript, JSON, Markdown, YAML (requires `pnpm install`) |
| `eslint`      | ESLint      | `.ts`, `.tsx` files (requires `pnpm install`)              |

## Tech Stack

| Layer    | Technology                                        |
| -------- | ------------------------------------------------- |
| Frontend | React, Vite, TypeScript, Tailwind, TanStack Query |
| Backend  | FastAPI, Python 3.13, Pydantic v2, SQLAlchemy 2.x |
| Database | PostgreSQL 16, Alembic                            |
| Cache    | Redis 7                                           |
| Storage  | MinIO                                             |
| Auth     | JWT + Refresh Tokens, RBAC                        |
| Infra    | Docker Compose, Nginx                             |
| CI/CD    | GitHub Actions                                    |
| Monorepo | pnpm workspaces, Turborepo                        |

## Documentation

- [Architecture](docs/architecture/overview.md)
- [Database ERD](docs/database/erd.md)
- [API Reference](docs/api/reference.md)
- [Authentication](docs/api/authentication.md)
- [Deployment](docs/deployment/guide.md)
- [Developer Guide](docs/developer-guide.md)
- [Coding Standards](docs/coding-standards.md)
- [Contributing](CONTRIBUTING.md)
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
