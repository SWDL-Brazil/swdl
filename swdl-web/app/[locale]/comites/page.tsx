import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import { ComitesContent } from '@/components/comites/ComitesContent';

export async function generateMetadata(): Promise<Metadata> {
  try {
    const t = await getTranslations('meta');
    return {
      title: t('comites_title'),
      description: t('comites_desc'),
    };
  } catch {
    return {
      title: 'Comitês — SWDL',
      description: 'Conheça os comitês e temas da SWDL 2026',
    };
  }
}

export default function ComitesPage() {
  return <ComitesContent />;
}
