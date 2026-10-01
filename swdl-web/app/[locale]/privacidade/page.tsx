import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import { PrivacidadeContent } from '@/components/legal/PrivacidadeContent';

export async function generateMetadata(): Promise<Metadata> {
  try {
    const t = await getTranslations('privacidade');
    return { title: t('page_title'), description: t('content') };
  } catch {
    return { title: 'Privacidade — SWDL', description: 'Como tratamos seus dados pessoais conforme a LGPD' };
  }
}

export default function PrivacidadePage() {
  return <PrivacidadeContent />;
}
