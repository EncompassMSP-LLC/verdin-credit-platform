import { apiPath, request } from './http';

export type OrganizationType = 'demo' | 'internal' | 'partner' | 'production';

export type OrgDemoFeature =
  'demo_data' | 'demo_notifications' | 'sample_borrowers' | 'fake_credit_reports' | 'training_mode';

export interface OrganizationContext {
  organization_id: string;
  name: string;
  slug: string;
  organization_type: OrganizationType;
  is_active: boolean;
  feature_flags: Record<string, boolean>;
  demo_capabilities_allowed: boolean;
  allow_demo_orgs: boolean;
  enable_sample_data: boolean;
  enable_demo_login: boolean;
  created_at: string;
}

export interface DemoSampleBorrowersResponse {
  created_client_ids: string[];
  organization_id: string;
  feature: OrgDemoFeature;
}

export async function getOrganizationContext(): Promise<OrganizationContext> {
  return request<OrganizationContext>(apiPath('/org-context'));
}

export async function upsertOrganizationFeatureFlag(payload: {
  feature: OrgDemoFeature;
  enabled: boolean;
}): Promise<OrganizationContext> {
  return request<OrganizationContext>(apiPath('/org-context/feature-flags'), {
    method: 'PUT',
    body: payload,
  });
}

export async function generateSampleBorrowers(count = 3): Promise<DemoSampleBorrowersResponse> {
  return request<DemoSampleBorrowersResponse>(apiPath('/org-context/demo/sample-borrowers'), {
    method: 'POST',
    body: { count },
  });
}

/** True when UI may show demo-only actions (never for production orgs). */
export function canShowDemoActions(ctx: OrganizationContext | null | undefined): boolean {
  if (!ctx) return false;
  return (
    ctx.demo_capabilities_allowed &&
    ctx.organization_type !== 'production' &&
    Boolean(ctx.feature_flags.sample_borrowers || ctx.feature_flags.demo_data)
  );
}
