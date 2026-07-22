'use client';

import { PageHeader } from '@/components/portal/PageHeader';
import { PortalCard } from '@/components/portal/PortalCard';
import { usePlatformAuth } from '@/lib/platform/auth';

export default function ProfilePage() {
  const { user } = usePlatformAuth();

  return (
    <div>
      <PageHeader
        eyebrow="Profile"
        title="Borrower profile"
        description="Identity from the shared client portal user record in the platform database."
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <PortalCard title="Portal account">
          <dl className="space-y-4 text-sm">
            <div>
              <dt className="text-slate-500">Display name</dt>
              <dd className="mt-1 font-medium">{user?.client_display_name ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Email</dt>
              <dd className="mt-1 font-medium">{user?.email ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Client ID</dt>
              <dd className="mt-1 font-mono text-xs">{user?.client_id ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Portal user ID</dt>
              <dd className="mt-1 font-mono text-xs">{user?.id ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Organization ID</dt>
              <dd className="mt-1 font-mono text-xs">{user?.organization_id ?? '—'}</dd>
            </div>
            <div>
              <dt className="text-slate-500">Last login</dt>
              <dd className="mt-1 font-medium">
                {user?.last_login_at ? new Date(user.last_login_at).toLocaleString() : '—'}
              </dd>
            </div>
          </dl>
        </PortalCard>

        <PortalCard title="How profile updates work">
          <p className="text-sm text-slate-500 dark:text-white/65">
            Contact and legal identity fields are managed on the Client record by staff in the
            operations app. Ask your case manager to update name, phone, or address. Portal
            email/password changes are also staff-mediated via Client → Portal user.
          </p>
        </PortalCard>
      </div>
    </div>
  );
}
