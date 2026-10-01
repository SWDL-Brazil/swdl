import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import { FacaParteContent } from '@/components/faca-parte/FacaParteContent';

export async function generateMetadata(): Promise<Metadata> {
  try {
    const t = await getTranslations('meta');
    return {
      title: t('faca_parte_title'),
      description: t('faca_parte_desc'),
    };
  } catch {
    return {
      title: 'Faça Parte — SWDL',
      description: 'Inscreva-se e participe da SWDL 2026',
    };
  }
}

export default function FacaPartePage() {
  return <FacaParteContent />;
}
