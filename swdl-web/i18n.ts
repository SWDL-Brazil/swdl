import { getRequestConfig } from 'next-intl/server';

export const locales = ['pt-BR', 'en', 'es', 'fr', 'de', 'it', 'nl', 'id', 'ms'] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = 'pt-BR';

export default getRequestConfig(async ({ requestLocale }) => {
  const requested = await requestLocale;
  const safeLocale = (locales as readonly string[]).includes(requested as string)
    ? (requested as Locale)
    : defaultLocale;

  return {
    locale: safeLocale,
    messages: (await import(`./messages/${safeLocale}.json`)).default,
  };
});
