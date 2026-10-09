import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { NewsMeta, type NewsLike } from './NewsCard';
import { resolveAssetUrl } from '@/lib/api';

interface CrisisFeedProps {
  items: NewsLike[];
}

export function CrisisFeed({ items }: CrisisFeedProps) {
  const t = useTranslations('noticias');
  const tc = useTranslations('common');
  if (items.length === 0) return null;

  return (
    <section className="py-10">
      <div className="section-rule">
        <div className="flex items-center gap-3">
          <span className="w-2 h-2 rounded-full bg-red-700 animate-pulse" />
          <h2>{t('section_live')}</h2>
        </div>
        <Link
          href="/noticias?cat=crise"
          className="text-xs font-mono uppercase tracking-[0.1em] text-[#7a5f1f] hover:text-[#4a380c] no-underline"
        >
          {t('category_crise')} →
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
        {items.slice(0, 4).map((item) => (
          <Link
            key={item.slug}
            href={`/noticia/${item.slug}`}
            className="group flex gap-4 no-underline items-start p-4 bg-white rounded-sm border border-red-600/15 hover:border-red-600/40 transition-colors"
          >
            <div className="overflow-hidden rounded-sm bg-surface-alt shrink-0">
              {item.image_url ? (
                <img
                  src={resolveAssetUrl(item.image_url)}
                  alt={item.title}
                  className="w-[140px] h-[100px] object-cover"
                  loading="lazy"
                />
              ) : (
                <div className="w-[140px] h-[100px] flex items-center justify-center bg-red-50 text-2xl">
                  ⚡
                </div>
              )}
            </div>
            <div className="min-w-0 flex-1">
              <span className="inline-flex items-center gap-1.5 font-mono text-[0.72rem] font-bold uppercase tracking-[0.12em] text-[#9a3412] mb-2">
                <span className="w-1.5 h-1.5 rounded-full bg-[#9a3412] animate-pulse" />
                {tc('live')}
              </span>
              <h3 className="font-display text-[16px] font-bold text-navy leading-snug line-clamp-3 group-hover:text-gold-dark transition-colors">
                {item.title}
              </h3>
              <NewsMeta item={item} showBadge={false} className="mt-2" />
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}
