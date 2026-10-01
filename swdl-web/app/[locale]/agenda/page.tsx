import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import { AgendaContent } from '@/components/agenda/AgendaContent';

export async function generateMetadata(): Promise<Metadata> {
  try {
    const t = await getTranslations('agenda');
    return {
      title: t('page_title'),
      description: t('hero_sub'),
    };
  } catch {
    return {
      title: 'Agenda — SWDL',
      description: 'Confira a programação completa do evento SWDL',
    };
  }
}

export default function AgendaPage() {
  return <AgendaContent />;
}
