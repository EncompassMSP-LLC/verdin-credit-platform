import { LOCALE_LABELS, setClientLocale, SUPPORTED_LOCALES, type SupportedLocale } from '@/i18n';
import { useTranslation } from 'react-i18next';

type LanguageSwitcherProps = {
  className?: string;
  /** Compact select for headers; default is a labeled control. */
  compact?: boolean;
};

export function LanguageSwitcher({ className = '', compact = false }: LanguageSwitcherProps) {
  const { i18n, t } = useTranslation('common');
  const current = (
    SUPPORTED_LOCALES.includes(i18n.language as SupportedLocale)
      ? i18n.language
      : i18n.language.startsWith('es')
        ? 'es'
        : 'en'
  ) as SupportedLocale;

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {!compact ? (
        <label htmlFor="client-locale" className="text-sm text-gray-600">
          {t('language.label')}
        </label>
      ) : null}
      <select
        id="client-locale"
        aria-label={t('language.label')}
        className="rounded-md border border-gray-300 bg-white px-2 py-1.5 text-sm text-gray-900 shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
        value={current}
        onChange={(event) => {
          void setClientLocale(event.target.value as SupportedLocale);
        }}
      >
        {SUPPORTED_LOCALES.map((locale) => (
          <option key={locale} value={locale}>
            {LOCALE_LABELS[locale]}
          </option>
        ))}
      </select>
    </div>
  );
}
