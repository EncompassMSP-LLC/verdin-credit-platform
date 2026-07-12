import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import enCommon from './locales/en/common.json';
import enEnrollment from './locales/en/enrollment.json';
import enPortal from './locales/en/portal.json';
import esCommon from './locales/es/common.json';
import esEnrollment from './locales/es/enrollment.json';
import esPortal from './locales/es/portal.json';

export const SUPPORTED_LOCALES = ['en', 'es'] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];

export const LOCALE_LABELS: Record<SupportedLocale, string> = {
  en: 'English',
  es: 'Español',
};

const STORAGE_KEY = 'verdin.clientLocale';

function detectLocale(): SupportedLocale {
  if (typeof window !== 'undefined') {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored === 'en' || stored === 'es') {
      return stored;
    }
    const browser = window.navigator.language.toLowerCase();
    if (browser.startsWith('es')) {
      return 'es';
    }
  }
  return 'en';
}

void i18n.use(initReactI18next).init({
  resources: {
    en: {
      common: enCommon,
      portal: enPortal,
      enrollment: enEnrollment,
    },
    es: {
      common: esCommon,
      portal: esPortal,
      enrollment: esEnrollment,
    },
  },
  lng: detectLocale(),
  fallbackLng: 'en',
  defaultNS: 'common',
  ns: ['common', 'portal', 'enrollment'],
  interpolation: {
    escapeValue: false,
  },
});

export function setClientLocale(locale: SupportedLocale) {
  if (typeof window !== 'undefined') {
    window.localStorage.setItem(STORAGE_KEY, locale);
  }
  void i18n.changeLanguage(locale);
  if (typeof document !== 'undefined') {
    document.documentElement.lang = locale;
  }
}

if (typeof document !== 'undefined') {
  document.documentElement.lang = i18n.language.startsWith('es') ? 'es' : 'en';
}

export default i18n;
