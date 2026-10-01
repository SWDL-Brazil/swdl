import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import { AvisoLegalContent } from '@/components/legal/AvisoLegalContent';

export async function generateMetadata(): Promise<Metadata> {
  try {
    const t = await getTranslations('aviso_legal');
    return { title: t('page_title'), description: t('content') };
  } catch {
    return { title: 'Aviso Legal — SWDL', description: 'Informações legais sobre o uso do site SWDL' };
  }
}

export default function AvisoLegalPage() {
  return <AvisoLegalContent />;
}
