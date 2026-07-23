import type { Config } from 'tailwindcss';

/**
 * Vol 23 design system — app-local tokens (FOUNDER-REVIEW P2-14).
 * Dark mode disabled for v1 (P2-13).
 */
const config: Config = {
  // Dark mode unused in v1 (FOUNDER-REVIEW P2-13); ThemeProvider forces light.
  darkMode: 'class',
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        lrp: {
          navy: '#00133E',
          gold: '#C29E5B',
          surface: '#F7F8FA',
          'surface-elevated': '#FFFFFF',
          border: '#D7DCE5',
          success: '#007860',
          warning: '#B45309',
          danger: '#B91C1C',
          info: '#1D4ED8',
        },
        navy: {
          900: '#00133E',
          800: '#001A4A',
          700: '#0A244F',
          600: '#163A6B',
        },
        gold: {
          700: '#8A6F3E',
          600: '#A88850',
          500: '#C29E5B',
          400: '#D0A848',
          300: '#E0C07A',
        },
        /** @deprecated prefer lrp.gold — kept for existing teal-* classnames */
        teal: {
          700: '#8A6F3E',
          600: '#C29E5B',
          500: '#D0A848',
          400: '#E0C07A',
        },
        emerald: {
          700: '#005848',
          600: '#007860',
          500: '#0A9A7A',
        },
        /** Product surfaces map to Vol 23 --lrp-surface (not cream) */
        sand: {
          50: '#F7F8FA',
          100: '#F7F8FA',
          200: '#EEF1F5',
        },
        ivory: {
          50: '#F7F8FA',
          100: '#F7F8FA',
          200: '#EEF1F5',
        },
        ink: {
          900: '#00133E',
          700: '#2A3550',
        },
        slate: {
          500: '#64748B',
          400: '#94A3B8',
        },
        success: '#007860',
        warning: '#B45309',
        critical: '#B91C1C',
      },
      fontFamily: {
        display: ['var(--font-display)', 'Georgia', 'serif'],
        sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-mono)', 'ui-monospace', 'monospace'],
      },
      maxWidth: {
        content: '72rem',
        prose: '42rem',
      },
      boxShadow: {
        soft: '0 1px 2px rgba(0, 19, 62, 0.06), 0 8px 24px rgba(0, 19, 62, 0.08)',
      },
      backgroundImage: {
        'path-gradient': 'linear-gradient(135deg, #00133E 0%, #0A244F 100%)',
        'progress-accent': 'linear-gradient(90deg, #C29E5B 0%, #E0C07A 100%)',
        'gold-line': 'linear-gradient(90deg, transparent, #C29E5B, transparent)',
      },
      letterSpacing: {
        eyebrow: '0.14em',
        brand: '0.18em',
      },
      borderRadius: {
        brand: '0.25rem',
      },
      transitionDuration: {
        brand: '200ms',
      },
    },
  },
  plugins: [],
};

export default config;
