import { NavLink, Outlet } from 'react-router-dom';
import { APP_NAME } from '@verdin/shared';
import { NotificationBell } from './NotificationBell';
import { useAuth } from '../lib/auth';
import { featureFlags } from '../lib/feature-flags';

const navItems = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/cases', label: 'Cases' },
  { to: '/clients', label: 'Clients' },
  { to: '/accounts', label: 'Accounts' },
  { to: '/documents', label: 'Documents' },
  ...(featureFlags.enableImports ? [{ to: '/imports/credit-report', label: 'Import Wizard' }] : []),
  ...(featureFlags.enableEnterprise
    ? [
        { to: '/compliance', label: 'Compliance' },
        { to: '/reporting', label: 'Reporting' },
        { to: '/org-admin', label: 'Org Admin' },
      ]
    : []),
  { to: '/timeline', label: 'Timeline' },
  { to: '/tasks', label: 'Tasks' },
  { to: '/settings', label: 'Settings' },
];

export function AppLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen">
      <aside className="w-64 bg-brand-900 text-white">
        <div className="border-b border-brand-700 px-6 py-5">
          <h1 className="text-lg font-bold">{APP_NAME}</h1>
          <p className="text-xs text-brand-100">v5.0.0-dev</p>
        </div>
        <nav className="px-3 py-4">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `mb-1 block rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-brand-700 text-white'
                    : 'text-brand-100 hover:bg-brand-700/50 hover:text-white'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="absolute bottom-0 w-64 border-t border-brand-700 p-4">
          <p className="truncate text-sm text-brand-100">
            {user?.first_name} {user?.last_name}
          </p>
          <p className="truncate text-xs text-brand-100/70">{user?.email}</p>
          <button
            onClick={logout}
            className="mt-2 text-xs text-brand-100 underline hover:text-white"
          >
            Sign out
          </button>
        </div>
      </aside>
      <main className="flex flex-1 flex-col overflow-auto">
        <header className="flex items-center justify-end border-b border-gray-200 bg-white px-6 py-3">
          <NotificationBell />
        </header>
        <div className="flex-1 overflow-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
