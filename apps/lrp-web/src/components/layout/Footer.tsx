import Image from 'next/image';
import Link from 'next/link';
import { Logo } from '@/components/brand/Logo';
import { Container } from '@/components/ui/Container';
import { footerNav, siteConfig } from '@/lib/site';

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-gold-500/30 bg-navy-900 text-white">
      <Container className="py-14 sm:py-16">
        <div className="grid gap-10 lg:grid-cols-[1.2fr_repeat(3,1fr)]">
          <div>
            <Logo variant="light" showTagline />
            <p className="mt-5 max-w-sm text-sm leading-relaxed text-white/70">
              Preparing today. Positioning tomorrow. Powering possibilities. We bridge readiness and
              opportunity through insight, technology, and trust.
            </p>
            <p className="mt-4 text-xs font-medium uppercase tracking-eyebrow text-gold-500">
              Intelligence · Innovation · Integrity · Impact
            </p>
            <p className="mt-4 text-sm text-white/60">
              <a
                className="underline-offset-2 hover:text-white hover:underline"
                href={`mailto:${siteConfig.email}`}
              >
                {siteConfig.email}
              </a>
            </p>
          </div>

          {(
            [
              ['Platform', footerNav.platform],
              ['Audiences', footerNav.audiences],
              ['Company', footerNav.company],
            ] as const
          ).map(([title, links]) => (
            <div key={title}>
              <h2 className="text-sm font-semibold uppercase tracking-wider text-white">{title}</h2>
              <div className="mt-2 h-px w-8 bg-gold-500" aria-hidden />
              <ul className="mt-4 space-y-2.5">
                {links.map((link) => (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      className="text-sm text-white/70 transition-colors hover:text-gold-400"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col gap-4 border-t border-gold-500/20 pt-8 sm:flex-row sm:items-end sm:justify-between">
          <div className="max-w-xl">
            <p className="text-xs font-medium uppercase tracking-eyebrow text-gold-500">
              Readiness is the strategy. Partnership is the advantage.
            </p>
            <p className="mt-3 text-xs leading-relaxed text-white/55">
              © {year} {siteConfig.name}. All rights reserved. {siteConfig.name}™ and the LRP mark
              are trademarks of their respective owners.
            </p>
          </div>
          <Image
            src="/brand/logo-icon.png"
            alt=""
            width={48}
            height={48}
            className="hidden h-12 w-12 rounded-brand bg-white/95 object-contain p-1 opacity-90 sm:block"
          />
        </div>
        <p className="mt-6 max-w-3xl text-xs leading-relaxed text-white/45">
          Lending Readiness Partners does not guarantee loan approval or funding decisions. Lender
          underwriting and applicable guidelines always govern.
        </p>
      </Container>
    </footer>
  );
}
