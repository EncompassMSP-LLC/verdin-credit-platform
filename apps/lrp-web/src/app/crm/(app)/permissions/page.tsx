'use client';

import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { PERMISSION_LABELS, ROLE_DEFINITIONS } from '@/lib/crm/permissions';
import type { CrmPermission } from '@/lib/crm/types';

export default function CrmPermissionsPage() {
  const allPermissions = Object.keys(PERMISSION_LABELS) as CrmPermission[];

  return (
    <RoleGate
      permission="permissions.manage"
      fallback={<p className="text-sm text-slate-500">Permission management required.</p>}
    >
      <PageHeader
        eyebrow="Governance"
        title="Role permissions"
        description="Enterprise RBAC matrix for the CRM edition. API-backed partner roles ship with Mortgage Partner APIs."
      />

      <div className="space-y-4">
        {ROLE_DEFINITIONS.map((def) => (
          <section
            key={def.role}
            className="rounded-md border border-navy-900/10 bg-white p-5 dark:border-white/10 dark:bg-navy-800"
          >
            <h2 className="text-base font-semibold">{def.label}</h2>
            <p className="mt-1 text-sm text-slate-600 dark:text-white/65">{def.description}</p>
            <p className="mt-2 text-xs text-slate-500">
              {def.permissions.length} / {allPermissions.length} permissions
            </p>
            <ul className="mt-3 flex flex-wrap gap-1.5">
              {allPermissions.map((perm) => {
                const allowed = def.permissions.includes(perm);
                return (
                  <li
                    key={perm}
                    className={
                      allowed
                        ? 'rounded bg-emerald-500/15 px-2 py-1 text-[0.7rem] font-medium text-emerald-800 dark:text-emerald-300'
                        : 'rounded bg-slate-100 px-2 py-1 text-[0.7rem] text-slate-400 dark:bg-white/5 dark:text-white/35'
                    }
                  >
                    {PERMISSION_LABELS[perm]}
                  </li>
                );
              })}
            </ul>
          </section>
        ))}
      </div>
    </RoleGate>
  );
}
