import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import { TermosContent } from '@/components/legal/TermosContent';

export async function generateMetadata(): Promise<Metadata> {
  try {
    const t = await getTranslations('termos');
    return { title: t('page_title'), description: t('content') };
  } catch {
    return { title: 'Termos de Uso — SWDL', description: 'Condições de uso do site e serviços SWDL' };
  }
}

export default function TermosPage() {
  return <TermosContent />;
}
