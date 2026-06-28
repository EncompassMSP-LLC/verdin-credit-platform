# Deployment Guide

## Prerequisites

- Docker and Docker Compose
- Node.js 20+ and pnpm 9+ (for local development)
- Python 3.13+ (for local API development)

## Docker Compose (Recommended)

```bash
# Clone and configure
git clone <repo-url>
cd verdin-credit-platform
cp .env.example .env

# Start entire stack
docker compose up -d

# Run migrations and seed
docker compose exec api alembic upgrade head
docker compose exec api python scripts/seed.py
```

### Services

| Service  | Port      | Description         |
| -------- | --------- | ------------------- |
| nginx    | 80        | Reverse proxy       |
| web      | 3000      | React frontend      |
| api      | 8000      | FastAPI backend     |
| postgres | 5432      | PostgreSQL database |
| redis    | 6379      | Cache and job queue |
| minio    | 9000/9001 | Object storage      |
| worker   | —         | Background jobs     |

## Environment Variables

See `.env.example` for all required variables. Critical production settings:

| Variable       | Description                    |
| -------------- | ------------------------------ |
| `SECRET_KEY`   | JWT signing key (min 32 chars) |
| `DATABASE_URL` | PostgreSQL connection string   |
| `CORS_ORIGINS` | Allowed frontend origins       |

## Production Checklist

- [ ] Set strong `SECRET_KEY` (use `openssl rand -hex 32`)
- [ ] Configure production database with SSL
- [ ] Set `APP_ENV=production`
- [ ] Configure HTTPS via Nginx or load balancer
- [ ] Set up database backups
- [ ] Configure monitoring and alerting
- [ ] Review CORS origins
