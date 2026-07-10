/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_ENABLE_AI?: string;
  readonly VITE_ENABLE_LLM?: string;
  readonly VITE_ENABLE_IMPORTS?: string;
  readonly VITE_ENABLE_ENTERPRISE?: string;
  readonly VITE_ENABLE_CLIENT_PORTAL?: string;
  readonly VITE_ENABLE_CLIENT_ENROLLMENT?: string;
  readonly VITE_ENABLE_PORTAL_PUSH?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
