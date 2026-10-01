'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { api, AgendaItem, EventPeriod } from '@/lib/api';
import { Container } from '@/components/ui/Container';
import { NowCard } from './NowCard';
import { Timeline } from './Timeline';

export function AgendaContent() {
  const t = useTranslations('agenda');
  const [items, setItems] = useState<AgendaItem[]>([]);
  const [periods, setPeriods] = useState<EventPeriod[]>([]);
  const [nowData, setNowData] = useState<{
    current: AgendaItem | null;
    next: AgendaItem | null;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadAgenda() {
      const [agendaData, agoraData, periodsData] = await Promise.all([
        api.agenda(),
        api.agendaAgora(),
        api.periods(),
      ]);
      if (cancelled) return;
      if (agendaData) setItems(agendaData);
      if (agoraData) setNowData(agoraData);
      if (periodsData) setPeriods(periodsData);
      setLoading(false);
    }

    loadAgenda();
    const id = setInterval(loadAgenda, 60000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  return (
    <div className="pt-[68px]">
      {/* PAGE HERO */}
      <section className="bg-navy py-16 relative overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <span className="font-display text-[120px] md:text-[200px] font-black text-white/[0.03] select-none">
            {t('hero_bg')}
          </span>
        </div>
        <Container>
          <div className="relative z-10">
            <div className="flex items-center gap-2 text-slate-light text-sm mb-4">
              <Link href="/" className="hover:text-white transition-colors">
                {t('breadcrumb_home')}
              </Link>
              <span aria-hidden>›</span>
              <span className="text-white">{t('breadcrumb_current')}</span>
            </div>
            <span className="section-label">
              <span className="w-7 h-px bg-gold" />
              {t('hero_label')}
            </span>
            <h1 className="font-display text-[clamp(36px,4vw,56px)] font-bold text-white mb-4">
              {t('hero_title')}
            </h1>
            <p className="text-slate-light text-lg max-w-2xl">{t('hero_desc')}</p>
          </div>
        </Container>
      </section>

      {/* PAGE MAIN */}
      <section className="bg-surface py-16 sm:py-[72px] sm:pb-24">
        <Container>
          {nowData?.current && (
            <NowCard current={nowData.current} next={nowData.next} />
          )}

          {loading ? (
            <div className="flex h-64 items-center justify-center">
              <span className="sr-only">{t('loading')}</span>
              <div className="h-8 w-8 animate-spin rounded-full border-2 border-gold border-t-transparent" />
            </div>
          ) : (
            <Timeline items={items} periods={periods} />
          )}
        </Container>
      </section>
    </div>
  );
}
