import type { RealtorUser } from '@/lib/realtor/types';
import { REALTOR_PERMISSIONS } from '@/lib/realtor/permissions';

/** Local demo realtor (LRP-301) — production builds never enable demo auth. */
export const DEMO_REALTOR_USERS: Array<RealtorUser & { password: string }> = [
  {
    id: 'demo-realtor-1',
    email: 'agent@lrp.realtor',
    password: 'changeme123',
    displayName: 'Alex Agent',
    organizationId: 'demo-realtor-org',
    organizationName: 'Summit Realty Partners',
    partnershipId: 'demo-realtor-partnership',
    partnershipDisplayName: 'Summit × LRP',
    permissions: [...REALTOR_PERMISSIONS],
    title: 'Realtor partner',
  },
];
