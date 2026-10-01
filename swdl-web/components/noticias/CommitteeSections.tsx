'use client';

import { useTranslations } from 'next-intl';
import { NewsCard, type NewsLike } from './NewsCard';
import { cn } from '@/lib/utils';

interface CommitteeSectionsProps {
  committees: string[];
  active: string;
  byCommittee: Record<string, NewsLike[]>;
  onSelect: (committee: string) => void;
}

export function CommitteeSections({
  committees,
  active,
  byCommittee,
  onSelect,
}: CommitteeSectionsProps) {
  const t = useTranslations('noticias');

  if (committees.length === 0) return null;

  const tabs = [{ slug: '', name: t('all_committees') }, ...committees.map((c) => ({ slug: c, name: c }))];
  const visible = active
    ? [{ slug: active, name: active, items: byCommittee[active] || [] }]
    : committees.map((c) => ({ slug: c, name: c, items: byCommittee[c] || [] }));

  return (
    <section className="py-10">
      <div className="section-rule">
        <h2>{t('tab_committees')}</h2>
        <div className="flex flex-wrap gap-1">
          {tabs.map((tab) => (
            <button
              key={tab.slug || 'all'}
              type="button"
              onClick={() => onSelect(tab.slug)}
              className={cn(
                'px-3 py-1 text-xs font-medium uppercase tracking-[0.08em] border-b-2 transition-colors',
                active === tab.slug
                  ? 'border-gold text-navy'
                  : 'border-transparent text-slate hover:text-navy'
              )}
            >
              {tab.name}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-8">
        {visible.map((col) => (
          <div key={col.slug} className="flex flex-col gap-6">
            <h3 className="font-mono text-xs tracking-[0.14em] uppercase text-[#7a5f1f] border-b border-navy/10 pb-2 m-0">
              {col.name}
            </h3>
            {col.items.length === 0 ? (
              <p className="text-sm text-slate">{t('empty')}</p>
            ) : (
              <div className="flex flex-col gap-5">
                {col.items.slice(0, 4).map((item) => (
                  <NewsCard
                    key={item.slug}
                    item={item}
                    imageHeight="sm"
                    layout="horizontal"
                  />
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
