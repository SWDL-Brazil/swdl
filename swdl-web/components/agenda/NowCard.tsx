'use client';

import { useTranslations } from 'next-intl';
import type { AgendaItem } from '@/lib/api';
import { formatTime } from '@/lib/utils';
import { Countdown } from './Countdown';

interface NowCardProps {
  current: AgendaItem | null;
  next: AgendaItem | null;
}

export function NowCard({ current, next }: NowCardProps) {
  const t = useTranslations('agenda');

  if (!current) return null;

  return (
    <div className="relative overflow-hidden rounded-md bg-navy px-5 py-6 sm:px-9 sm:py-8 mb-12 grid gap-6 lg:grid-cols-[1fr_auto] items-center">
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background: 'radial-gradient(circle at 85% 50%, rgba(201,168,76,0.12) 0%, transparent 60%)',
        }}
      />

      <div className="relative z-[1] min-w-0">
        <div className="inline-flex items-center gap-2 font-mono text-[0.72rem] font-bold tracking-[0.14em] uppercase text-gold mb-2.5">
          <span className="h-2 w-2 shrink-0 rounded-full bg-gold animate-pulse shadow-[0_0_0_0_rgba(201,168,76,0.6)]" />
          <span>
            {t('now_label')}
            {current.day ? ` · ${t('day_n', { n: current.day })}` : ''}
          </span>
        </div>
        <div className="font-display text-[clamp(20px,3vw,26px)] font-bold text-white mb-1.5">
          {current.title}
        </div>
        <div className="flex flex-wrap items-center gap-x-5 gap-y-1.5 text-[13px] text-slate-light">
          {current.location && (
            <span className="inline-flex items-center gap-1.5">📍 {current.location}</span>
          )}
          <span className="inline-flex items-center gap-1.5">
            ⏱ {t('started_at')} {formatTime(current.start_time)}
          </span>
          {current.end_time && (
            <span className="inline-flex items-center gap-1.5">
              ⏳ {t('ends_at')} {formatTime(current.end_time)}
            </span>
          )}
        </div>
      </div>

      {next && (
        <div className="relative z-[1] text-left lg:text-right">
          <span className="block font-mono text-[0.68rem] tracking-[0.12em] uppercase text-white/35 mb-1">
            {t('now_next_label')}
          </span>
          <div className="text-sm font-semibold text-white mb-0.5">{next.title}</div>
          <div className="font-mono text-xs text-gold mb-2">{formatTime(next.start_time)}</div>
          <Countdown targetTime={next.start_time} />
        </div>
      )}
    </div>
  );
}
