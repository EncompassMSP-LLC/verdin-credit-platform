import {
  LayoutDashboard,
  Building2,
  Users,
  Landmark,
  Home,
  ListTodo,
  GitBranch,
  KanbanSquare,
  Bot,
  MessageSquare,
  Mail,
  LineChart,
  UserPlus,
  CalendarDays,
  FileStack,
  StickyNote,
  Settings2,
  Shield,
  type LucideIcon,
} from 'lucide-react';
import type { CrmNavIcon as IconName } from '@/lib/crm/nav';

const icons: Record<IconName, LucideIcon> = {
  dashboard: LayoutDashboard,
  partners: Building2,
  borrowers: Users,
  lenders: Landmark,
  realtors: Home,
  tasks: ListTodo,
  workflow: GitBranch,
  pipeline: KanbanSquare,
  automations: Bot,
  sms: MessageSquare,
  email: Mail,
  reporting: LineChart,
  referrals: UserPlus,
  calendar: CalendarDays,
  documents: FileStack,
  notes: StickyNote,
  admin: Settings2,
  permissions: Shield,
};

export function CrmNavIcon({ name, className }: { name: IconName; className?: string }) {
  const Icon = icons[name];
  return <Icon className={className} aria-hidden />;
}
