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
    <div>
      {/* PAGE HERO */}
      <section className="relative overflow-hidden bg-navy pt-[68px] min-h-[260px] flex items-end">
        <div
          className="pointer-events-none absolute inset-0"
          style={{
            background:
              'radial-gradient(circle at 80% 50%, rgba(201,168,76,0.10) 0%, transparent 60%)',
          }}
        />
        <div
          className="pointer-events-none absolute right-[-20px] bottom-[-20px] font-display text-[clamp(72px,18vw,160px)] font-black text-white/3 leading-none whitespace-nowrap select-none"
          aria-hidden
        >
          {t('hero_bg')}
        </div>

        <div className="relative z-[1] w-full px-6 sm:px-12 py-10 sm:py-11">
          <div className="container">
            <nav className="flex items-center gap-2 font-mono text-[0.72rem] tracking-[0.1em] uppercase text-white/35 mb-4">
              <Link href="/" className="text-white/35 hover:text-white transition-colors no-underline">
                {t('breadcrumb_home')}
              </Link>
              <span aria-hidden>›</span>
              <span className="text-gold">{t('breadcrumb_current')}</span>
            </nav>
            <div className="section-label mb-2.5">{t('hero_label')}</div>
            <h1 className="font-display text-[clamp(36px,5vw,60px)] font-black leading-none text-white">
              {t('hero_title')}
            </h1>
            <p className="mt-2.5 max-w-[520px] text-[15px] leading-relaxed text-slate-light">
              {t('hero_desc')}
            </p>
          </div>
        </div>
      </section>

      {/* PAGE MAIN */}
      <main className="bg-surface py-16 sm:py-[72px] sm:pb-24">
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
      </main>
    </div>
  );
}
