# Staff web app (`apps/web`)

React + Vite + TypeScript UI (TanStack Query, Tailwind). Client portal routes are gated by `VITE_ENABLE_CLIENT_PORTAL`.

## Run (Docker)

Built as a static nginx image. Feature flags are **bake-time** `VITE_*` build args from repo-root `.env`:

```bash
docker compose build web
docker compose up -d web
```

App: http://localhost:3000 (or http://localhost via nginx)

After changing `VITE_*` flags, **rebuild** the web image.

## Run (host / Vite)

```bash
pnpm --filter @verdin/api-client build   # when client types change
pnpm --filter @verdin/web dev
```

Vite reads `VITE_*` from repo-root `.env` (or `apps/web/.env.local`). Dev server: http://localhost:5173

## Feature flags

See `src/lib/feature-flags.ts`. Backend `ENABLE_*` and frontend `VITE_ENABLE_*` should stay aligned for the same capability.

## Related

- [Developer guide](../../docs/developer-guide.md)
- [Root README — environment files](../../README.md)
- [`@verdin/api-client`](../../packages/api-client/README.md)
