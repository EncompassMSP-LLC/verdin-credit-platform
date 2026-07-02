export type FeatureFlag =
  'ENABLE_AI' | 'ENABLE_LLM' | 'ENABLE_IMPORTS' | 'ENABLE_ENTERPRISE' | 'ENABLE_CLIENT_PORTAL';

const VITE_ENV_KEYS: Record<FeatureFlag, keyof ImportMetaEnv> = {
  ENABLE_AI: 'VITE_ENABLE_AI',
  ENABLE_LLM: 'VITE_ENABLE_LLM',
  ENABLE_IMPORTS: 'VITE_ENABLE_IMPORTS',
  ENABLE_ENTERPRISE: 'VITE_ENABLE_ENTERPRISE',
  ENABLE_CLIENT_PORTAL: 'VITE_ENABLE_CLIENT_PORTAL',
};

function parseEnvBoolean(value: string | undefined): boolean {
  if (value === undefined || value === '') {
    return false;
  }

  return ['true', '1', 'yes', 'on'].includes(value.toLowerCase());
}

export function isFeatureEnabled(flag: FeatureFlag): boolean {
  const envKey = VITE_ENV_KEYS[flag];
  return parseEnvBoolean(import.meta.env[envKey]);
}

export const featureFlags = {
  enableAi: isFeatureEnabled('ENABLE_AI'),
  enableLlm: isFeatureEnabled('ENABLE_LLM'),
  enableImports: isFeatureEnabled('ENABLE_IMPORTS'),
  enableEnterprise: isFeatureEnabled('ENABLE_ENTERPRISE'),
  enableClientPortal: isFeatureEnabled('ENABLE_CLIENT_PORTAL'),
} as const;
