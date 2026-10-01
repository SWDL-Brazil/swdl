'use client';

import { useTranslations, useLocale } from 'next-intl';
import Link from 'next/link';
import type { NewsLike } from './NewsCard';
import { formatTimeAgo } from '@/lib/format';

interface NewsSidebarProps {
  trending: NewsLike[];
}

export function NewsSidebar({ trending }: NewsSidebarProps) {
  const t = useTranslations('noticias');
  const locale = useLocale();

  if (trending.length === 0) return null;

  return (
    <aside className="sticky top-[140px] flex flex-col gap-6">
      <div className="bg-white rounded-sm border border-navy/10 p-5">
        <h3 className="font-display text-lg font-bold text-navy m-0 mb-4 pb-3 border-b-4 border-t border-navy/10 border-t-4 pt-3">
          {t('trending')}
        </h3>
        <ol className="list-none p-0 m-0 flex flex-col gap-4">
          {trending.slice(0, 5).map((item, i) => (
            <li key={item.slug}>
              <Link
                href={`/noticia/${item.slug}`}
                className="group flex gap-3 no-underline items-start"
              >
                <span className="shrink-0 w-7 h-7 rounded-sm bg-gold text-navy font-mono text-xs font-bold flex items-center justify-center">
                  {i + 1}
                </span>
                <div className="min-w-0">
                  <h4 className="font-display text-sm font-bold text-navy leading-snug line-clamp-3 group-hover:text-gold-dark transition-colors m-0">
                    {item.title}
                  </h4>
                  {formatTimeAgo(item.created_at, locale, item.time_ago) && (
                    <span className="news-meta mt-1 block">
                      {formatTimeAgo(item.created_at, locale, item.time_ago)}
                    </span>
                  )}
                </div>
              </Link>
            </li>
          ))}
        </ol>
      </div>

      <div className="bg-navy rounded-sm p-5 text-white">
        <p className="font-mono text-[0.75rem] uppercase tracking-[0.12em] text-gold mb-2">
          SWDL
        </p>
        <p className="text-sm text-slate-light leading-relaxed mb-4">
          {t('sidebar_about')}
        </p>
        <Link
          href="/sobre"
          className="btn-ghost-white text-xs px-4 py-2"
        >
          {t('sidebar_more')}
        </Link>
      </div>
    </aside>
  );
}
