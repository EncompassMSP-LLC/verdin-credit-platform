import type { LucideIcon } from 'lucide-react';
import {
  Bell,
  BookOpen,
  Bot,
  ClipboardList,
  FileText,
  Gauge,
  LayoutDashboard,
  MessageSquare,
  Scale,
  Settings,
  TrendingUp,
  UserRound,
  Waypoints,
} from 'lucide-react';
import type { PortalNavItem } from '@/lib/portal/nav';

const map: Record<PortalNavItem['icon'], LucideIcon> = {
  dashboard: LayoutDashboard,
  timeline: Waypoints,
  score: Gauge,
  tasks: ClipboardList,
  documents: FileText,
  messages: MessageSquare,
  disputes: Scale,
  ai: Bot,
  progress: TrendingUp,
  learning: BookOpen,
  notifications: Bell,
  profile: UserRound,
  settings: Settings,
};

export function PortalNavIcon({
  name,
  className,
}: {
  name: PortalNavItem['icon'];
  className?: string;
}) {
  const Icon = map[name];
  return <Icon className={className} aria-hidden />;
}
