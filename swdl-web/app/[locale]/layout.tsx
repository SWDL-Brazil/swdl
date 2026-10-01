import { NextIntlClientProvider } from 'next-intl';
import { getMessages, getTranslations } from 'next-intl/server';
import type { Metadata } from 'next';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';
import { Ticker } from '@/components/layout/Ticker';
import { CrisisBanner } from '@/components/layout/CrisisBanner';

export async function generateMetadata(): Promise<Metadata> {
  try {
    const t = await getTranslations('meta');
    const title = t('root_title');
    const description = t('root_desc');
    return {
      title,
      description,
      keywords: ['Model UN', 'ONU', 'SESI', 'Diplomacia', 'Simulação', 'Debate'],
      openGraph: {
        title,
        description,
        url: 'https://swdl.vercel.app',
        siteName: 'SWDL',
        type: 'website',
      },
    };
  } catch {
    return {
      title: 'SWDL — SESI World Diplomacy League',
      description:
        'O maior simulado de relações internacionais do SESI. Represente nações, debata resoluções e construa acordos diplomáticos.',
    };
  }
}

export default async function LocaleLayout({
  children,
  params: { locale },
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  const messages = await getMessages();

  return (
    <html lang={locale} suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html:
              "try{if(localStorage.getItem('swdl-cvd')==='1'){document.documentElement.setAttribute('data-cvd','true')}}catch(e){}",
          }}
        />
      </head>
      <body className="font-body bg-surface text-navy overflow-x-hidden antialiased">
        <NextIntlClientProvider messages={messages}>
          <CrisisBanner />
          <Navbar />
          <Ticker />
          <main className="min-h-screen">{children}</main>
          <Footer />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
