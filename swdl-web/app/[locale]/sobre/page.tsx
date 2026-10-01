import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import { SobreContent } from '@/components/sobre/SobreContent';

export async function generateMetadata(): Promise<Metadata> {
  try {
    const t = await getTranslations('meta');
    return {
      title: t('sobre_title'),
      description: t('sobre_desc'),
    };
  } catch {
    return {
      title: 'Sobre — SWDL',
      description: 'Conheça a história e missão da SWDL',
    };
  }
}

export default function SobrePage() {
  return <SobreContent />;
}
