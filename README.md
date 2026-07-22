# Ultimate Credit Repair LLC

> Current release: **[v27.0.0](docs/release-notes/v27.0.0.md)** — Dispute Playbook Depth & Case Entity Re-resolve

Enterprise credit operations platform: case management, document intelligence (OCR + credit-report parsers including IdentityIQ), dispute workflows, reinvestigation analytics, compliance tooling, and gated enterprise integrations.

**Source of truth for product status:** [`docs/roadmap/README.md`](docs/roadmap/README.md) · [`docs/governance/capability-matrix.md`](docs/governance/capability-matrix.md)

## Quick Start

```bash
# Install dependencies
pnpm install

# Configure environment (repo-root .env — see "Environment files" below)
cp .env.example .env

# Start the full local stack
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
| admin@verdin.demo | changeme123 | Admin |

### Staff guides

- [Dispute workflow (step-by-step)](docs/guides/dispute-workflow.md) — import reports, cross-bureau compare, prepare letters, mail-ready export

## Environment files

| File                          | Used by                                                                                                    | Notes                                                                                   |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| **`.env`** (repo root)        | Docker Compose variable substitution (`${VITE_*}` web build args); hybrid local API/Vite when cwd finds it | Copy from `.env.example`. This is the file used for day-to-day local work.              |
| **`.env.example`**            | Template only                                                                                              | Commit-safe defaults                                                                    |
| **`.env.production`**         | Local pilot / production-like stacks                                                                       | Used with `docker compose -f docker-compose.local-pilot.yml --env-file .env.production` |
| **`.env.production.example`** | Template for production                                                                                    | Secrets go here for pilot; never commit real secrets                                    |

**Important:** `docker-compose.yml` hard-codes core API/worker DB/Redis/MinIO settings in the `environment:` blocks. Feature flags (`ENABLE_*`) from root `.env` are **not** automatically injected into the API container unless you add them to compose or run the API on the host. Web feature flags (`VITE_*`) **are** read from root `.env` at **image build** time via Compose `${…}` substitution.

See [`docs/developer-guide.md`](docs/developer-guide.md) for hybrid (host Vite + Docker Postgres/Redis) setup.

## Repository Structure

```
verdin-credit-platform/
├── apps/
│   ├── api/                 # FastAPI backend
│   ├── web/                 # React + Vite staff UI (+ portal when enabled)
│   └── worker/              # Background job processor (OCR, parse, resolve, …)
├── packages/
│   ├── api-client/          # Typed HTTP client for web
│   ├── shared/              # Shared TypeScript types
│   ├── ui/                  # Shared React components
│   ├── validation/          # Shared Zod schemas
│   ├── report-parsers/      # Experian / Equifax / TransUnion / ACR / IdentityIQ
│   ├── job-orchestrator/    # Worker job queue helpers
│   ├── llm-gateway/         # LLM policy + provider gate (ADR-012)
│   ├── document-classification/
│   ├── document-metadata/
│   ├── entity-resolution/
│   ├── event-bus/
│   └── event-types/
├── infrastructure/          # nginx, postgres init, scripts
├── docs/                    # Roadmap, governance, API, deployment, ADRs
├── tests/                   # Repo-level e2e + credit-report fixtures
├── .github/workflows/
├── .cursor/rules/           # Version sprint-loop agent rules
├── AGENTS.md
├── docker-compose.yml
├── docker-compose.local-pilot.yml
└── docker-compose.prod.yml
```

## Development

```bash
# Run all apps in dev mode (host)
pnpm dev

# Lint and typecheck
pnpm lint
pnpm typecheck

# API tests (use test DB)
cd apps/api
# PowerShell: $env:DATABASE_URL="postgresql+asyncpg://verdin:verdin@localhost:5432/verdin_credit_test"
python -m pytest

# Format
pnpm format
```

Build `@verdin/api-client` before web typecheck when client types change:

```bash
pnpm --filter @verdin/api-client build
pnpm --filter @verdin/web typecheck
```

### Pre-commit Hooks

```bash
pip install pre-commit
pnpm install
cd apps/api && pip install -r requirements.txt
pre-commit install
pre-commit run --all-files
```

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

- [Docs hub](docs/README.md)
- [Product roadmap](docs/roadmap/README.md)
- [Capability matrix](docs/governance/capability-matrix.md)
- [API reference](docs/api/reference.md)
- [Developer guide](docs/developer-guide.md)
- [Deployment](docs/deployment/guide.md)
- [Engineering changelog](docs/engineering/changelog.md)
- [Release notes — v27.0.0](docs/release-notes/v27.0.0.md)
- [Architecture](docs/architecture/README.md)
- [AGENTS.md](AGENTS.md) — AI development instructions

## Roadmap (high level)

Shipped through **v27.0.0** (Compliance Intelligence Phase 26). Next planned milestone is **Version 28.0 — Monitoring Report Parser Depth** (IdentityIQ golden fixtures, SmartCredit parser). Live bureau polling and automated filing remain deferred pending legal/compliance sign-off.

Full table: [`docs/roadmap/README.md`](docs/roadmap/README.md).

## License

MIT — see [LICENSE](LICENSE)
