import type { User } from '@verdin/api-client';
import type { LenderRole, LenderUser } from '@/lib/lender/types';

/**
 * Interim mapping: staff JWT → lender workspace roles.
 * True partner-member JWT (mortgage_partner) remains deferred (Vol 24).
 */
export function mapStaffRoleToLender(role: User['role']): LenderRole {
  switch (role) {
    case 'owner':
    case 'admin':
      return 'lender_admin';
    case 'case_manager':
      return 'credit_ops';
    case 'reviewer':
      return 'underwriter_view';
    case 'read_only':
    default:
      return 'read_only';
  }
}

export function mapStaffUserToLender(user: User): LenderUser {
  const displayName =
    [user.first_name, user.last_name].filter(Boolean).join(' ').trim() || user.email;
  return {
    id: user.id,
    email: user.email,
    displayName,
    role: mapStaffRoleToLender(user.role),
    organizationId: user.organization_id ?? 'unknown',
    organizationName: 'Lending Readiness Partners',
    title: user.role.replace(/_/g, ' '),
  };
}
