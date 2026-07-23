export type PortalNavItem = {
  href: string;
  label: string;
  icon:
    | 'dashboard'
    | 'timeline'
    | 'score'
    | 'tasks'
    | 'documents'
    | 'messages'
    | 'disputes'
    | 'ai'
    | 'progress'
    | 'learning'
    | 'notifications'
    | 'profile'
    | 'settings';
  badge?: number;
};

export const portalNav: PortalNavItem[] = [
  { href: '/portal/dashboard', label: 'Dashboard', icon: 'dashboard' },
  { href: '/portal/timeline', label: 'Credit Timeline', icon: 'timeline' },
  { href: '/portal/readiness', label: 'Readiness Score', icon: 'score' },
  { href: '/portal/tasks', label: 'Tasks', icon: 'tasks', badge: 4 },
  { href: '/portal/documents', label: 'Documents', icon: 'documents' },
  { href: '/portal/messages', label: 'Messages', icon: 'messages', badge: 2 },
  { href: '/portal/disputes', label: 'Disputes', icon: 'disputes' },
  { href: '/portal/ai-analysis', label: 'AI Credit Analysis', icon: 'ai' },
  { href: '/portal/progress', label: 'Progress Tracker', icon: 'progress' },
  { href: '/portal/learning', label: 'Learning Center', icon: 'learning' },
  { href: '/portal/notifications', label: 'Notifications', icon: 'notifications', badge: 3 },
  { href: '/portal/profile', label: 'Profile', icon: 'profile' },
  { href: '/portal/settings', label: 'Settings', icon: 'settings' },
];
