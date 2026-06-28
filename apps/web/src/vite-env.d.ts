/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_ENABLE_AI?: string;
  readonly VITE_ENABLE_IMPORTS?: string;
  readonly VITE_ENABLE_ENTERPRISE?: string;
  readonly VITE_ENABLE_CLIENT_PORTAL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
