/** Advisory overlays until dedicated readiness APIs are on the portal realm. */
export const readinessScore = {
  overall: 72,
  band: 'Near Ready',
  updatedAt: '2026-07-20',
  trend: +6,
  dimensions: [
    { key: 'payment', label: 'Payment History', score: 78, weight: 0.28 },
    { key: 'utilization', label: 'Credit Utilization', score: 64, weight: 0.22 },
    { key: 'mix', label: 'Account Mix', score: 71, weight: 0.12 },
    { key: 'age', label: 'Age of Credit', score: 68, weight: 0.12 },
    { key: 'inquiries', label: 'Inquiries', score: 75, weight: 0.1 },
    { key: 'public', label: 'Public Records / Collections', score: 58, weight: 0.16 },
  ],
  blockers: [
    {
      id: 'b1',
      title: 'Medical collection — Metro Health',
      impact: 'High',
      action: 'Verify accuracy and prepare staff-mediated dispute package',
    },
    {
      id: 'b2',
      title: 'Revolving utilization above 40%',
      impact: 'Medium',
      action: 'Pay down card ending 4821 below 30% before next pull',
    },
    {
      id: 'b3',
      title: 'Missing YTD income documentation',
      impact: 'Medium',
      action: 'Upload most recent pay stubs and W-2',
    },
  ],
};

export const timelineEvents = [
  {
    id: 't1',
    date: '2026-07-20',
    title: 'Readiness score recalculated',
    detail: 'Overall readiness moved from 66 to 72 after utilization improvement.',
    type: 'score' as const,
  },
  {
    id: 't2',
    date: '2026-07-14',
    title: 'Dispute package submitted for review',
    detail: 'Staff-mediated review started for Metro Health collection.',
    type: 'dispute' as const,
  },
  {
    id: 't3',
    date: '2026-07-08',
    title: 'Document uploaded',
    detail: 'Driver license and proof of address verified.',
    type: 'document' as const,
  },
  {
    id: 't4',
    date: '2026-06-29',
    title: 'Onboarding complete',
    detail: 'Borrower goals captured and baseline readiness established.',
    type: 'milestone' as const,
  },
  {
    id: 't5',
    date: '2026-06-22',
    title: 'Credit file imported',
    detail: 'Tri-bureau snapshot linked to your readiness workspace.',
    type: 'credit' as const,
  },
];

export const tasks = [
  {
    id: 'task-1',
    title: 'Upload June–July pay stubs',
    due: '2026-07-24',
    status: 'open' as const,
    priority: 'high' as const,
    category: 'Documents',
  },
  {
    id: 'task-2',
    title: 'Confirm Metro Health account details',
    due: '2026-07-25',
    status: 'open' as const,
    priority: 'high' as const,
    category: 'Disputes',
  },
  {
    id: 'task-3',
    title: 'Complete learning module: Utilization basics',
    due: '2026-07-28',
    status: 'open' as const,
    priority: 'medium' as const,
    category: 'Learning',
  },
  {
    id: 'task-4',
    title: 'Respond to advisor message',
    due: '2026-07-23',
    status: 'open' as const,
    priority: 'medium' as const,
    category: 'Messages',
  },
  {
    id: 'task-5',
    title: 'Review readiness score explanation',
    due: '2026-07-21',
    status: 'done' as const,
    priority: 'low' as const,
    category: 'Readiness',
  },
];

export const documents = [
  {
    id: 'doc-1',
    name: 'Government ID — Driver License.pdf',
    category: 'Identity',
    uploadedAt: '2026-07-08',
    status: 'verified' as const,
    size: '1.2 MB',
  },
  {
    id: 'doc-2',
    name: 'Proof of Address — Utility Bill.pdf',
    category: 'Identity',
    uploadedAt: '2026-07-08',
    status: 'verified' as const,
    size: '840 KB',
  },
  {
    id: 'doc-3',
    name: 'W-2 2025.pdf',
    category: 'Income',
    uploadedAt: '2026-07-12',
    status: 'in_review' as const,
    size: '620 KB',
  },
  {
    id: 'doc-4',
    name: 'Collection statement — Metro Health.pdf',
    category: 'Disputes',
    uploadedAt: '2026-07-14',
    status: 'in_review' as const,
    size: '1.0 MB',
  },
];

export const conversations = [
  {
    id: 'msg-1',
    from: 'Alex Rivera',
    role: 'Case Manager',
    preview:
      'I’ve queued your dispute package for staff review. Please confirm the account number.',
    updatedAt: '2026-07-21T14:20:00Z',
    unread: true,
    messages: [
      {
        id: 'm1',
        from: 'Alex Rivera',
        body: 'Jordan — your readiness score improved after the card paydown. Next focus is the Metro Health collection.',
        at: '2026-07-20T16:00:00Z',
      },
      {
        id: 'm2',
        from: 'You',
        body: 'Thanks. I uploaded the statement yesterday. What else do you need from me?',
        at: '2026-07-20T18:12:00Z',
      },
      {
        id: 'm3',
        from: 'Alex Rivera',
        body: 'I’ve queued your dispute package for staff review. Please confirm the account number ending in 3391 matches your records.',
        at: '2026-07-21T14:20:00Z',
      },
    ],
  },
  {
    id: 'msg-2',
    from: 'Sam Okonkwo',
    role: 'Loan Officer',
    preview: 'Once utilization stays under 30% for a cycle, we can reassess pre-approval timing.',
    updatedAt: '2026-07-18T11:05:00Z',
    unread: true,
    messages: [
      {
        id: 'm4',
        from: 'Sam Okonkwo',
        body: 'Once utilization stays under 30% for a cycle, we can reassess pre-approval timing. No need to rush an offer yet.',
        at: '2026-07-18T11:05:00Z',
      },
    ],
  },
];

export const disputes = [
  {
    id: 'dsp-1',
    account: 'Metro Health Collection',
    bureau: 'Experian',
    status: 'In staff review',
    openedAt: '2026-07-14',
    nextStep: 'Advisor validates packet completeness before mediated filing prep',
  },
  {
    id: 'dsp-2',
    account: 'Legacy Retail Charge-off',
    bureau: 'Equifax',
    status: 'Evidence requested',
    openedAt: '2026-06-30',
    nextStep: 'Upload original account statements if available',
  },
];

export const aiInsights = [
  {
    id: 'ai-1',
    title: 'Utilization is your fastest controllable lever',
    confidence: 0.86,
    summary:
      'Bringing revolving balances under 30% is projected to improve readiness more quickly than waiting on collection aging alone.',
    actions: ['Schedule a paydown plan for card 4821', 'Avoid new revolving opens this quarter'],
  },
  {
    id: 'ai-2',
    title: 'Collection item warrants mediated review',
    confidence: 0.79,
    summary:
      'The Metro Health tradeline shows characteristics often associated with furnish errors. Staff review is recommended before any filing preparation.',
    actions: ['Confirm account number', 'Attach statement already uploaded'],
  },
  {
    id: 'ai-3',
    title: 'Documentation gap may delay lender handoff',
    confidence: 0.74,
    summary:
      'Income documentation is incomplete relative to your stated purchase timeline. Upload remaining stubs to keep readiness exportable.',
    actions: ['Upload 2 most recent pay stubs'],
  },
];

export const progressMilestones = [
  { id: 'p1', label: 'Profile & goals captured', complete: true, date: '2026-06-29' },
  { id: 'p2', label: 'Identity documents verified', complete: true, date: '2026-07-08' },
  { id: 'p3', label: 'Baseline readiness established', complete: true, date: '2026-06-29' },
  { id: 'p4', label: 'High-impact blockers identified', complete: true, date: '2026-07-01' },
  { id: 'p5', label: 'Utilization remediation in progress', complete: false, date: null },
  { id: 'p6', label: 'Collection dispute package ready', complete: false, date: null },
  { id: 'p7', label: 'Lending-ready export for lender review', complete: false, date: null },
];

export const learningModules = [
  {
    id: 'learn-1',
    title: 'What “lending ready” actually means',
    minutes: 8,
    level: 'Foundations',
    completed: true,
  },
  {
    id: 'learn-2',
    title: 'Credit utilization without the jargon',
    minutes: 10,
    level: 'Foundations',
    completed: false,
  },
  {
    id: 'learn-3',
    title: 'How staff-mediated disputes protect you',
    minutes: 9,
    level: 'Disputes',
    completed: false,
  },
  {
    id: 'learn-4',
    title: 'Working with your realtor on honest timelines',
    minutes: 7,
    level: 'Partners',
    completed: false,
  },
];

export const notifications = [
  {
    id: 'n1',
    title: 'New advisor message',
    body: 'Alex Rivera asked you to confirm an account number.',
    at: '2026-07-21T14:21:00Z',
    read: false,
    href: '/portal/messages',
  },
  {
    id: 'n2',
    title: 'Task due soon',
    body: 'Upload June–July pay stubs by Jul 24.',
    at: '2026-07-21T09:00:00Z',
    read: false,
    href: '/portal/tasks',
  },
  {
    id: 'n3',
    title: 'Readiness score updated',
    body: 'Your overall readiness is now 72 (Near Ready).',
    at: '2026-07-20T12:00:00Z',
    read: false,
    href: '/portal/readiness',
  },
  {
    id: 'n4',
    title: 'Document verified',
    body: 'Proof of address was marked verified.',
    at: '2026-07-08T15:40:00Z',
    read: true,
    href: '/portal/documents',
  },
];

export const creditAccounts = [
  {
    id: 'acc-1',
    name: 'Harbor Bank Visa',
    type: 'Revolving',
    balance: 4200,
    limit: 9000,
    status: 'Open',
    note: 'Utilization 47% — paydown recommended',
  },
  {
    id: 'acc-2',
    name: 'Auto Loan — SouthPoint',
    type: 'Installment',
    balance: 12800,
    limit: null,
    status: 'Current',
    note: 'On-time 24 months',
  },
  {
    id: 'acc-3',
    name: 'Metro Health',
    type: 'Collection',
    balance: 1860,
    limit: null,
    status: 'Collection',
    note: 'Primary readiness blocker',
  },
];
