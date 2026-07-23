'use client';

import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard } from '@/components/portal/PortalCard';
import { RoleGate } from '@/components/lender/RoleGate';
import { PERMISSION_LABELS, ROLE_DEFINITIONS } from '@/lib/lender/permissions';
import type { LenderPermission } from '@/lib/lender/types';
import { cn } from '@/lib/utils';

const PERMISSIONS = Object.keys(PERMISSION_LABELS) as LenderPermission[];

export default function PermissionsPage() {
  return (
    <RoleGate permission="permissions.manage">
      <div>
        <PageHeader
          eyebrow="Role permissions"
          title="Access matrix"
          description="Demo RBAC for the lender workspace. Production will sync from Mortgage Partner org settings."
        />

        <PortalCard title="Permission matrix">
          <div className="overflow-x-auto">
            <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
              <thead>
                <tr>
                  <th
                    scope="col"
                    className="sticky left-0 z-10 border-b border-navy-900/10 bg-[#F8FAFC] px-3 py-2.5 text-[0.65rem] font-semibold uppercase tracking-wider text-slate-500 dark:border-white/10 dark:bg-navy-900/60"
                  >
                    Permission
                  </th>
                  {ROLE_DEFINITIONS.map((role) => (
                    <th
                      key={role.role}
                      scope="col"
                      className="border-b border-navy-900/10 px-3 py-2.5 text-[0.65rem] font-semibold uppercase tracking-wider text-slate-500 dark:border-white/10"
                    >
                      <span className="block">{role.label}</span>
                      <span className="mt-1 block font-normal normal-case text-slate-400">
                        {role.role}
                      </span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {PERMISSIONS.map((permission) => (
                  <tr key={permission}>
                    <th
                      scope="row"
                      className="sticky left-0 z-10 border-b border-navy-900/8 bg-white px-3 py-2.5 text-left font-normal dark:border-white/8 dark:bg-navy-800/80"
                    >
                      <span className="block text-sm text-navy-900 dark:text-white">
                        {PERMISSION_LABELS[permission]}
                      </span>
                      <span className="text-[0.65rem] text-slate-400">{permission}</span>
                    </th>
                    {ROLE_DEFINITIONS.map((role) => {
                      const allowed = role.permissions.includes(permission);
                      return (
                        <td
                          key={`${role.role}-${permission}`}
                          className="border-b border-navy-900/8 px-3 py-2.5 text-center dark:border-white/8"
                        >
                          <span
                            className={cn(
                              'inline-flex h-6 w-6 items-center justify-center rounded-md text-xs font-bold',
                              allowed
                                ? 'bg-emerald-600/15 text-emerald-700 dark:text-emerald-400'
                                : 'bg-navy-900/5 text-slate-300 dark:bg-white/5 dark:text-white/20',
                            )}
                            aria-label={allowed ? 'Allowed' : 'Denied'}
                          >
                            {allowed ? '✓' : '—'}
                          </span>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {ROLE_DEFINITIONS.map((role) => (
              <div
                key={role.role}
                className="rounded-md border border-navy-900/8 bg-[#F8FAFC] p-4 dark:border-white/10 dark:bg-navy-900/40"
              >
                <p className="font-semibold text-navy-900 dark:text-white">{role.label}</p>
                <p className="mt-1 text-xs text-slate-500">{role.description}</p>
                <p className="mt-2 text-xs text-slate-400">
                  {role.permissions.length} permissions granted
                </p>
              </div>
            ))}
          </div>
        </PortalCard>
      </div>
    </RoleGate>
  );
}
