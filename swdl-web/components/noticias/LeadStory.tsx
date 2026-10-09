import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { NewsMeta, type NewsLike } from './NewsCard';
import { cn } from '@/lib/utils';
import { categoryLabelKey } from '@/lib/format';
import { resolveAssetUrl } from '@/lib/api';

interface LeadStoryProps {
  item: NewsLike;
  className?: string;
}

export function LeadStory({ item, className }: LeadStoryProps) {
  const t = useTranslations('noticias');
  const tc = useTranslations('common');
  const href = `/noticia/${item.slug}`;
  const excerpt =
    item.excerpt ||
    (item.body ? item.body.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim().slice(0, 220) : '');

  return (
    <Link
      href={href}
      className={cn(
        'group grid grid-cols-1 md:grid-cols-2 gap-6 items-center no-underline pb-8 border-b border-navy/10',
        className
      )}
    >
      <div className="order-2 md:order-1">
        <div className="flex items-center gap-2 mb-3">
          <span className="news-kicker">
            {categoryLabelKey(item.category_slug)
              ? t(categoryLabelKey(item.category_slug)!)
              : item.category}
          </span>
          {item.is_crisis && (
            <span className="inline-flex items-center gap-1.5 font-mono text-[0.72rem] font-bold uppercase tracking-[0.12em] text-[#9a3412]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#9a3412] animate-pulse" />
              {tc('live')}
            </span>
          )}
        </div>
        <h2 className="font-display text-[clamp(26px,3vw,36px)] font-bold text-navy leading-[1.12] mb-3 line-clamp-4 group-hover:text-gold-dark transition-colors">
          {item.title}
        </h2>
        {excerpt && (
          <p className="text-[15px] leading-relaxed text-slate line-clamp-3 mb-4">
            {excerpt}
          </p>
        )}
        <NewsMeta item={item} showBadge={false} />
      </div>

      <div className="order-1 md:order-2 overflow-hidden rounded-sm bg-surface-alt">
        {item.image_url ? (
          <img
            src={resolveAssetUrl(item.image_url)}
            alt={item.title}
            className="w-full h-[220px] md:h-[420px] object-cover transition-transform duration-500 group-hover:scale-[1.03]"
            loading="eager"
          />
        ) : (
          <div className="w-full h-[220px] md:h-[420px] flex items-center justify-center text-5xl bg-navy/5">
            📰
          </div>
        )}
      </div>
    </Link>
  );
}
