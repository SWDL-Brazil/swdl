import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import { NoticiasContent } from '@/components/noticias/NoticiasContent';

export async function generateMetadata(): Promise<Metadata> {
  try {
    const t = await getTranslations('noticias');
    return {
      title: t('page_title'),
      description: t('hero_sub'),
    };
  } catch {
    return {
      title: 'Notícias — SWDL',
      description: 'Acompanhe as últimas novidades da SWDL',
    };
  }
}

export default function NoticiasPage() {
  return <NoticiasContent />;
}
