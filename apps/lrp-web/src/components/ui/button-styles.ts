import { cn } from '@/lib/utils';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'inverse';
type ButtonSize = 'md' | 'lg';

const variants: Record<ButtonVariant, string> = {
  primary: 'bg-gold-500 text-navy-900 hover:bg-gold-400 focus-visible:outline-gold-500 shadow-sm',
  secondary:
    'bg-white text-navy-900 ring-1 ring-inset ring-navy-900/15 hover:bg-sand-50 focus-visible:outline-navy-700',
  ghost: 'bg-transparent text-navy-900 hover:bg-navy-900/5 focus-visible:outline-navy-700',
  inverse: 'bg-gold-500 text-navy-900 hover:bg-gold-400 focus-visible:outline-gold-400',
};

const sizes: Record<ButtonSize, string> = {
  md: 'px-5 py-2.5 text-sm tracking-wide',
  lg: 'px-6 py-3 text-base tracking-wide',
};

export function buttonClasses(
  variant: ButtonVariant = 'primary',
  size: ButtonSize = 'md',
  className?: string,
): string {
  return cn(
    'inline-flex items-center justify-center gap-2 rounded-brand font-semibold uppercase transition-colors duration-200',
    'disabled:pointer-events-none disabled:opacity-50',
    variants[variant],
    sizes[size],
    className,
  );
}
