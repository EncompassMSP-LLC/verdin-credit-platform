import { NavLink, Outlet } from 'react-router-dom';
import { APP_NAME } from '@verdin/shared';
import { AppShell, Main, Sidebar } from '@verdin/ui';
import { useAuth } from '../lib/auth';

const navItems = [
  { to: '/', label: 'Dashboard', end: true },
  { to: '/cases', label: 'Cases' },
  { to: '/accounts', label: 'Accounts' },
  { to: '/documents', label: 'Documents' },
  { to: '/tasks', label: 'Tasks' },
  { to: '/settings', label: 'Settings' },
];

export function AppLayout() {
  const { user, logout } = useAuth();

  return (
    <AppShell>
      <Sidebar className="bg-brand-900 text-white">
        <div className="border-b border-brand-700 px-6 py-5">
          <h1 className="text-lg font-bold">{APP_NAME}</h1>
          <p className="text-xs text-brand-100">v4.2.0</p>
        </div>
        <nav className="flex-1 px-3 py-4">
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
        <div className="border-t border-brand-700 p-4">
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
      </Sidebar>
      <Main>
        <Outlet />
      </Main>
    </AppShell>
  );
}
