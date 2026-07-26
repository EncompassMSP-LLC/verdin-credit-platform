'use client';

import { useMemo, useState } from 'react';
import { DataTable } from '@/components/lender/DataTable';
import { PageHeader } from '@/components/crm/PageHeader';
import { RoleGate } from '@/components/crm/RoleGate';
import { useCrmAuth } from '@/lib/crm/auth';
import { partners as seedPartners } from '@/lib/crm/data';
import {
  pickPrimaryPartnership,
  useCreateCrmPartnerContact,
  useCrmMortgagePartnerStatus,
  useCrmPartnerContacts,
  useCrmPartnerships,
  type Partnership,
} from '@/lib/crm/partner-hooks';

type PartnerRow = {
  id: string;
  name: string;
  type: string;
  status: string;
  market: string;
  primaryContact: string;
  ownerName: string;
  activeReferrals: number;
  fundedYtd: number;
};

function platformRow(row: Partnership): PartnerRow {
  return {
    id: row.id,
    name: row.display_name,
    type: row.partner_type,
    status: row.status,
    market: '—',
    primaryContact: row.primary_contact_name?.trim() || '—',
    ownerName: '—',
    activeReferrals: row.active_referral_count ?? 0,
    fundedYtd: 0,
  };
}

/**
 * Spec: Vol 21 · partners hub · LRP-101
 * Platform auth → mortgage_partner partnerships + contacts; demo → seed rows.
 */
export default function CrmPartnersPage() {
  const { authMode, can } = useCrmAuth();
  const statusQuery = useCrmMortgagePartnerStatus();
  const partnershipsQuery = useCrmPartnerships();
  const selected = pickPrimaryPartnership(partnershipsQuery.data);
  const contactsQuery = useCrmPartnerContacts(selected?.id);
  const createContact = useCreateCrmPartnerContact(selected?.id);

  const isDemo = authMode === 'demo';
  const platformEnabled = statusQuery.data?.mortgage_partner_enabled === true;
  const canManage = can('partners.manage');

  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [isPrimary, setIsPrimary] = useState(true);
  const [formError, setFormError] = useState<string | null>(null);
  const [formOk, setFormOk] = useState<string | null>(null);

  const loading =
    !isDemo &&
    (statusQuery.isLoading || partnershipsQuery.isLoading || (selected && contactsQuery.isLoading));

  const errorMessage = useMemo(() => {
    if (isDemo || loading) return null;
    if (statusQuery.isError || partnershipsQuery.isError) {
      return 'Could not load partnerships. Confirm the API is running and ENABLE_MORTGAGE_PARTNER=true.';
    }
    if (!platformEnabled) return 'Mortgage Partner edition is not enabled on this API.';
    if (!partnershipsQuery.data?.length) {
      return 'No partnerships found for this organization yet. Create a partnership via API to populate this list.';
    }
    return null;
  }, [
    isDemo,
    loading,
    statusQuery.isError,
    partnershipsQuery.isError,
    platformEnabled,
    partnershipsQuery.data,
  ]);

  const rows = useMemo((): PartnerRow[] => {
    if (isDemo) {
      return seedPartners.map((p) => ({
        id: p.id,
        name: p.name,
        type: p.type,
        status: p.status,
        market: p.market,
        primaryContact: p.primaryContact,
        ownerName: p.ownerName,
        activeReferrals: p.activeReferrals,
        fundedYtd: p.fundedYtd,
      }));
    }
    if (errorMessage) return [];
    return (partnershipsQuery.data ?? []).map(platformRow);
  }, [isDemo, errorMessage, partnershipsQuery.data]);

  async function onCreateContact(event: React.FormEvent) {
    event.preventDefault();
    setFormError(null);
    setFormOk(null);
    if (!selected) {
      setFormError('Select a partnership first.');
      return;
    }
    try {
      await createContact.mutateAsync({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: email.trim() || null,
        contact_role: 'loan_officer',
        is_primary: isPrimary,
      });
      setFirstName('');
      setLastName('');
      setEmail('');
      setFormOk('Contact saved.');
    } catch {
      setFormError('Could not create contact. Admin write access is required.');
    }
  }

  return (
    <RoleGate
      permission="partners.view"
      fallback={<p className="text-sm text-slate-500">No access to partners.</p>}
    >
      <PageHeader
        eyebrow="Relationships"
        title="Partners"
        description="Lender, realtor, broker, and operator organizations with ownership and referral health."
      />

      {isDemo ? (
        <p className="mb-4 rounded-brand border border-gold-500/30 bg-gold-500/10 px-4 py-3 text-sm text-navy-900">
          Demo mode — showing sample partners. Sign in with a platform staff account to load live
          partnerships and contacts.
        </p>
      ) : null}

      {errorMessage ? (
        <p className="mb-4 rounded-brand border border-critical/30 bg-critical/10 px-4 py-3 text-sm text-critical">
          {errorMessage}
        </p>
      ) : null}

      {loading ? <p className="mb-4 text-sm text-slate-500">Loading partners…</p> : null}

      <div className="rounded-md border border-navy-900/10 bg-white dark:border-white/10 dark:bg-navy-800">
        <DataTable
          rows={rows}
          columns={[
            {
              key: 'name',
              header: 'Partner',
              cell: (r) => (
                <div>
                  <p className="font-medium">{r.name}</p>
                  <p className="text-xs text-slate-500">{r.type}</p>
                </div>
              ),
            },
            { key: 'status', header: 'Status', cell: (r) => r.status },
            { key: 'market', header: 'Market', cell: (r) => r.market },
            { key: 'contact', header: 'Primary', cell: (r) => r.primaryContact },
            { key: 'owner', header: 'Owner', cell: (r) => r.ownerName },
            {
              key: 'refs',
              header: 'Active refs',
              cell: (r) => String(r.activeReferrals),
            },
            {
              key: 'funded',
              header: 'Funded YTD',
              cell: (r) => String(r.fundedYtd),
            },
          ]}
        />
      </div>

      {!isDemo && selected && canManage ? (
        <div className="mt-8 space-y-4">
          <h2 className="text-sm font-semibold text-navy-900">
            Contacts — {selected.display_name}
          </h2>
          {contactsQuery.isError ? (
            <p className="text-sm text-critical">Could not load contacts for this partnership.</p>
          ) : null}
          <ul className="space-y-2 text-sm text-slate-700">
            {(contactsQuery.data ?? []).map((c) => (
              <li
                key={c.id}
                className="rounded-md border border-navy-900/10 bg-white px-3 py-2 dark:border-white/10 dark:bg-navy-800"
              >
                <span className="font-medium">
                  {c.first_name} {c.last_name}
                </span>
                {c.is_primary ? (
                  <span className="ml-2 text-xs uppercase tracking-wide text-gold-700">
                    Primary
                  </span>
                ) : null}
                <span className="ml-2 text-slate-500">
                  {c.contact_role}
                  {c.email ? ` · ${c.email}` : ''}
                </span>
              </li>
            ))}
            {!contactsQuery.isLoading && !(contactsQuery.data ?? []).length ? (
              <li className="text-slate-500">No contacts yet.</li>
            ) : null}
          </ul>

          <form onSubmit={onCreateContact} className="grid max-w-xl gap-3 sm:grid-cols-2">
            <div>
              <label htmlFor="contact-first" className="block text-xs font-medium">
                First name
              </label>
              <input
                id="contact-first"
                required
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="mt-1 w-full rounded-md border border-lrp-border bg-lrp-surface-elevated px-3 py-2 text-sm"
              />
            </div>
            <div>
              <label htmlFor="contact-last" className="block text-xs font-medium">
                Last name
              </label>
              <input
                id="contact-last"
                required
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="mt-1 w-full rounded-md border border-lrp-border bg-lrp-surface-elevated px-3 py-2 text-sm"
              />
            </div>
            <div className="sm:col-span-2">
              <label htmlFor="contact-email" className="block text-xs font-medium">
                Email
              </label>
              <input
                id="contact-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 w-full rounded-md border border-lrp-border bg-lrp-surface-elevated px-3 py-2 text-sm"
              />
            </div>
            <label className="flex items-center gap-2 text-sm sm:col-span-2">
              <input
                type="checkbox"
                checked={isPrimary}
                onChange={(e) => setIsPrimary(e.target.checked)}
              />
              Set as primary contact
            </label>
            {formError ? <p className="text-sm text-critical sm:col-span-2">{formError}</p> : null}
            {formOk ? <p className="text-sm text-emerald-700 sm:col-span-2">{formOk}</p> : null}
            <button
              type="submit"
              disabled={createContact.isPending}
              className="rounded-md bg-navy-900 px-4 py-2 text-sm font-semibold text-white hover:bg-navy-700 disabled:opacity-60 sm:col-span-2 sm:w-fit"
            >
              {createContact.isPending ? 'Saving…' : 'Add contact'}
            </button>
          </form>
        </div>
      ) : null}
    </RoleGate>
  );
}
