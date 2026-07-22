import {
  LayoutDashboard,
  UserPlus,
  Users,
  Gauge,
  KanbanSquare,
  FileStack,
  MessagesSquare,
  LineChart,
  CalendarRange,
  Download,
  Bell,
  Settings2,
  Shield,
  type LucideIcon,
} from 'lucide-react';
import type { LenderNavIcon as IconName } from '@/lib/lender/nav';

const icons: Record<IconName, LucideIcon> = {
  dashboard: LayoutDashboard,
  referrals: UserPlus,
  borrowers: Users,
  readiness: Gauge,
  pipeline: KanbanSquare,
  documents: FileStack,
  messages: MessagesSquare,
  analytics: LineChart,
  reports: CalendarRange,
  exports: Download,
  notifications: Bell,
  admin: Settings2,
  permissions: Shield,
};

export function LenderNavIcon({ name, className }: { name: IconName; className?: string }) {
  const Icon = icons[name];
  return <Icon className={className} aria-hidden />;
}
