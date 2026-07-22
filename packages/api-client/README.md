# `@verdin/api-client`

Typed HTTP client used by `apps/web` (and portal) to call the FastAPI backend.

## Build

```bash
pnpm --filter @verdin/api-client build
```

**Always rebuild this package before web typecheck** when API client types or exports change:

```bash
pnpm --filter @verdin/api-client build
pnpm --filter @verdin/web typecheck
```

## Usage

```ts
import { configureApiClient, … } from '@verdin/api-client';

configureApiClient({ baseUrl: import.meta.env.VITE_API_BASE_URL });
```

Source: `src/` (accounts, cases, documents, reporting, compliance, …).

## Related

- [API reference](../../docs/api/reference.md)
- [apps/web README](../../apps/web/README.md)
