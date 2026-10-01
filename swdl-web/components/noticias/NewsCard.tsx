import Link from 'next/link';
import { useTranslations, useLocale } from 'next-intl';
import { CommitteeDot, Badge } from '@/components/ui/Badge';
import { cn } from '@/lib/utils';
import { formatTimeAgo, categoryLabelKey } from '@/lib/format';

export type NewsLike = {
  slug: string;
  title: string;
  category: string;
  category_slug: string;
  committee?: string;
  is_crisis?: boolean;
  image_url?: string | null;
  time_ago?: string;
  created_at?: string | null;
  excerpt?: string;
  body?: string;
};

const categoryColors: Record<string, 'crise' | 'oficial' | 'imprensa' | 'votacao'> = {
  crise: 'crise',
  oficial: 'oficial',
  imprensa: 'imprensa',
  votacao: 'votacao',
};

export function NewsMeta({
  item,
  showBadge = true,
  className,
}: {
  item: NewsLike;
  showBadge?: boolean;
  className?: string;
}) {
  const t = useTranslations('noticias');
  const locale = useLocale();
  const catKey = categoryLabelKey(item.category_slug);
  const time = formatTimeAgo(item.created_at, locale, item.time_ago);

  return (
    <div className={cn('flex flex-wrap items-center gap-2 text-slate', className)}>
      {item.committee && item.committee !== 'geral' && (
        <>
          <CommitteeDot committee={item.committee} />
          <span className="news-meta">{item.committee}</span>
          <span className="meta-sep">|</span>
        </>
      )}
      {showBadge && (
        <Badge variant={categoryColors[item.category_slug] || 'default'}>
          {catKey ? t(catKey) : item.category}
        </Badge>
      )}
      {time && <span className="news-meta">{time}</span>}
    </div>
  );
}

interface NewsCardProps {
  item: NewsLike;
  href?: string;
  className?: string;
  imageHeight?: 'sm' | 'md' | 'lg';
  showExcerpt?: boolean;
  showImage?: boolean;
  layout?: 'vertical' | 'horizontal';
}

const heights = {
  sm: 'h-[80px] w-[110px]',
  md: 'h-[180px] w-full',
  lg: 'h-[240px] w-full',
};

export function NewsCard({
  item,
  href,
  className,
  imageHeight = 'md',
  showExcerpt = false,
  showImage = true,
  layout = 'vertical',
}: NewsCardProps) {
  const link = href || `/noticia/${item.slug}`;
  const horizontal = layout === 'horizontal';

  return (
    <Link
      href={link}
      className={cn(
        'group no-underline h-full min-w-0',
        horizontal ? 'flex flex-row gap-4 items-start' : 'flex flex-col',
        className
      )}
    >
      {showImage && item.image_url && (
        <div
          className={cn(
            'overflow-hidden rounded-sm bg-surface-alt shrink-0',
            !horizontal && 'mb-3 self-stretch'
          )}
        >
          <img
            src={item.image_url}
            alt={item.title}
            className={cn(
              'object-cover transition-transform duration-500 group-hover:scale-[1.03]',
              horizontal ? heights.sm : heights[imageHeight],
              horizontal && 'w-[110px]'
            )}
            loading="lazy"
          />
        </div>
      )}
      <div className={cn('min-w-0', horizontal ? 'flex-1' : 'flex flex-col flex-1')}>
        <NewsMeta item={item} className="mb-2" />
        <h3
          className={cn(
            'news-title m-0 line-clamp-3 group-hover:text-gold-dark transition-colors',
            imageHeight === 'lg' || horizontal ? 'text-[17px]' : 'text-[18px]',
            !horizontal && imageHeight === 'lg' && 'text-[20px]'
          )}
        >
          {item.title}
        </h3>
        {showExcerpt && (item.excerpt || item.body) && (
          <p className="text-sm text-slate leading-relaxed mt-2 mb-0 line-clamp-3">
            {item.excerpt || item.body!.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim().slice(0, 160)}
          </p>
        )}
      </div>
    </Link>
  );
}
