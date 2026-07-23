import type { User } from '@verdin/api-client';
import type { CrmRole, CrmUser } from '@/lib/crm/types';

/** Map platform staff RBAC → CRM edition roles (Vol 21 / E1). */
export function mapStaffRoleToCrm(role: User['role']): CrmRole {
  switch (role) {
    case 'owner':
    case 'admin':
      return 'crm_admin';
    case 'case_manager':
      return 'ops_coordinator';
    case 'reviewer':
      return 'loan_officer';
    case 'read_only':
    default:
      return 'read_only';
  }
}

export function mapStaffUserToCrm(user: User): CrmUser {
  const displayName =
    [user.first_name, user.last_name].filter(Boolean).join(' ').trim() || user.email;
  return {
    id: user.id,
    email: user.email,
    displayName,
    role: mapStaffRoleToCrm(user.role),
    organizationId: user.organization_id ?? 'unknown',
    organizationName: 'Lending Readiness Partners',
    title: user.role.replace(/_/g, ' '),
  };
}
