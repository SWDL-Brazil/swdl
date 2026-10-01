'use client';

import { useLocale, useTranslations } from 'next-intl';
import type { AgendaItem, EventPeriod } from '@/lib/api';
import { formatDate, formatShortDate, formatTime } from '@/lib/utils';
import { periodColor, statusMeta } from './status';

interface TimelineProps {
  items: AgendaItem[];
  periods: EventPeriod[];
}

interface DateGroup {
  key: string;
  items: AgendaItem[];
}

interface PeriodGroup {
  periodId: number | 'sem-periodo';
  period?: EventPeriod;
  dateGroups: DateGroup[];
}

function groupItems(items: AgendaItem[], periods: EventPeriod[]): PeriodGroup[] {
  const byPeriod = new Map<number | 'sem-periodo', AgendaItem[]>();
  for (const item of items) {
    const pid = item.period_id ?? 'sem-periodo';
    const list = byPeriod.get(pid) || [];
    list.push(item);
    byPeriod.set(pid, list);
  }

  const groups: PeriodGroup[] = [];
  for (const [pid, periodItems] of Array.from(byPeriod.entries())) {
    const period =
      pid === 'sem-periodo' ? undefined : periods.find((p) => p.id === pid) || undefined;

    const byDate = new Map<string, AgendaItem[]>();
    for (const item of periodItems) {
      const key = item.event_date || 'sem-data';
      const list = byDate.get(key) || [];
      list.push(item);
      byDate.set(key, list);
    }

    const dateGroups: DateGroup[] = Array.from(byDate.entries())
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([key, dateItems]) => ({
        key,
        items: [...dateItems].sort((a, b) => {
          if (a.order !== b.order) return a.order - b.order;
          return (a.start_time || '').localeCompare(b.start_time || '');
        }),
      }));

    groups.push({ periodId: pid, period, dateGroups });
  }

  // Mantém ordem natural dos períodos (sem período no fim se misturado)
  groups.sort((a, b) => {
    if (a.periodId === 'sem-periodo') return 1;
    if (b.periodId === 'sem-periodo') return -1;
    return 0;
  });

  return groups;
}

function PeriodSeparator({ period }: { period?: EventPeriod }) {
  const t = useTranslations('agenda');
  const color = periodColor(period?.color);
  const name = period?.name || t('no_period');
  const range =
    period?.start_date && period?.end_date
      ? `${formatShortDate(period.start_date)} — ${formatShortDate(period.end_date)}`
      : '';

  return (
    <div className="flex items-center gap-3.5 pt-7 pb-2">
      <div className="h-0.5 flex-1 rounded opacity-35" style={{ background: color }} />
      <span
        className="shrink-0 rounded-full px-3.5 py-1.5 text-[13px] font-semibold text-white tracking-[0.03em] whitespace-nowrap"
        style={{ background: color }}
      >
        {name}
      </span>
      {range && (
        <span className="shrink-0 text-xs text-slate whitespace-nowrap">{range}</span>
      )}
      <div className="h-0.5 flex-1 rounded opacity-35" style={{ background: color }} />
    </div>
  );
}

function DateSeparator({ dateKey }: { dateKey: string }) {
  const t = useTranslations('agenda');
  const locale = useLocale();
  const label =
    dateKey && dateKey !== 'sem-data' ? formatDate(dateKey, locale) : t('no_date');

  return (
    <div className="flex items-center gap-4 my-10 first:mt-0">
      <div className="h-px flex-1 bg-navy/10" />
      <span className="rounded-[20px] border border-navy/10 bg-surface-alt px-4 py-1.5 font-mono text-[0.7rem] font-bold tracking-[0.1em] uppercase text-navy whitespace-nowrap">
        {label}
      </span>
      <div className="h-px flex-1 bg-navy/10" />
    </div>
  );
}

function TimelineItem({ item }: { item: AgendaItem }) {
  const t = useTranslations('agenda');
  const meta = statusMeta(item.status);
  const tag = t(meta.tagKey);
  const isPast = meta.cls === 'past';
  const isCurrent = meta.cls === 'current';
  const isArchive = meta.cls === 'archive';

  const itemCls = isArchive
    ? 'opacity-100'
    : isPast
      ? 'opacity-45'
      : 'opacity-100';

  const bodyCls = isCurrent
    ? 'bg-gold/5 border-l-[3px] border-gold -ml-px'
    : isArchive
      ? ''
      : '';

  const tagCls = (() => {
    switch (meta.tagCls) {
      case 'tag-now':
        return 'bg-gold text-navy';
      case 'tag-done':
        return isArchive
          ? 'bg-slate/15 text-slate border border-slate/30'
          : 'bg-slate text-white';
      case 'tag-next':
        return 'bg-navy text-white';
      case 'tag-break':
        return 'bg-slate-700 text-white';
      case 'tag-vote':
        return 'bg-green-700 text-white cvd-chip';
      case 'tag-crisis':
        return 'bg-red-700 text-white cvd-chip';
      case 'tag-award':
        return 'bg-navy text-white';
      default:
        return 'bg-navy text-white';
    }
  })();

  const timeCls = isCurrent
    ? 'text-gold-dark font-bold'
    : isPast || isArchive
      ? 'text-slate'
      : 'text-slate';

  const titleCls = isPast || isArchive ? 'text-[#4B5563]' : 'text-navy';

  return (
    <div className={`grid grid-cols-1 sm:grid-cols-[120px_1fr] relative transition-opacity ${itemCls}`}>
      <div className="relative pt-6 sm:pt-6 sm:pr-5 sm:text-right max-sm:pt-4 max-sm:pb-1">
        <span className={`font-mono text-xs font-medium leading-none ${timeCls}`}>
          {formatTime(item.start_time)}
        </span>
        <div
          className={`hidden sm:block absolute right-[-5px] top-7 w-2.5 h-2.5 rounded-full border-2 z-[1] ${
            isCurrent
              ? 'bg-gold border-gold shadow-[0_0_0_4px_rgba(201,168,76,0.2)] w-3 h-3 right-[-6px] top-[27px]'
              : isPast || isArchive
                ? 'bg-slate border-slate'
                : 'bg-surface border-navy/10'
          }`}
        />
      </div>

      <div
        className={`py-5 border-b border-navy/10 last:border-b-0 max-sm:border-l-[3px] max-sm:border-navy/10 max-sm:pl-4 max-sm:pb-5 ${bodyCls}`}
      >
        <span
          className={`inline-flex items-center gap-1.5 font-mono text-[0.62rem] font-bold tracking-[0.1em] uppercase px-2.5 py-[3px] rounded-sm mb-2 ${tagCls}`}
        >
          {tag}
        </span>
        <div className={`font-display text-lg font-bold leading-tight mb-1.5 ${titleCls}`}>
          {item.title}
        </div>
        {item.description && (
          <p className="text-[13px] text-[#4B5563] leading-[1.65] max-w-[640px] mb-2.5">
            {item.description}
          </p>
        )}
        <div className="flex flex-wrap items-center gap-4 mt-1.5">
          {item.location && (
            <span className="inline-flex items-center gap-1.5 text-xs text-[#4B5563]">
              📍 {item.location}
            </span>
          )}
          {item.committee && (
            <span className="font-mono text-[0.68rem] tracking-[0.08em] uppercase px-2.5 py-[3px] rounded-sm bg-navy/7 text-navy">
              {item.committee}
            </span>
          )}
          {item.end_time && (
            <span className="inline-flex items-center gap-1.5 text-xs text-[#4B5563]">
              ⏳ {t('until')} {formatTime(item.end_time)}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export function Timeline({ items, periods }: TimelineProps) {
  const t = useTranslations('agenda');
  const locale = useLocale();

  if (!items.length) {
    return (
      <div className="py-12 text-center text-sm text-[#4B5563]">{t('empty')}</div>
    );
  }

  const groups = groupItems(items, periods);

  return (
    <div className="relative flex flex-col">
      <div
        className="hidden sm:block absolute left-[108px] top-0 bottom-0 w-px bg-navy/10"
        aria-hidden
      />

      {groups.map((group) => {
        const key =
          group.periodId === 'sem-periodo'
            ? `p-sem-${group.dateGroups.map((d) => d.key).join('-')}`
            : `p-${group.periodId}`;

        return (
          <div key={key}>
            <PeriodSeparator period={group.period} />
            {group.dateGroups.map((dg) => (
              <div key={`${key}-${dg.key}`}>
                <DateSeparator dateKey={dg.key} />
                <div>
                  {dg.items.map((item) => (
                    <TimelineItem key={item.id} item={item} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
}
