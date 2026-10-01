'use client';

import { useTranslations } from 'next-intl';
import { NewsCard, type NewsLike } from './NewsCard';

interface ArchiveListProps {
  items: NewsLike[];
  hasMore: boolean;
  onLoadMore: () => void;
}

export function ArchiveList({ items, hasMore, onLoadMore }: ArchiveListProps) {
  const t = useTranslations('noticias');

  if (items.length === 0) {
    return <p className="text-slate py-8">{t('empty')}</p>;
  }

  return (
    <div>
      <div className="flex flex-col divide-y divide-navy/10">
        {items.map((item) => (
          <NewsCard
            key={item.slug}
            item={item}
            imageHeight="sm"
            showExcerpt
            layout="horizontal"
            className="py-5 border-b-0"
          />
        ))}
      </div>

      {hasMore && (
        <div className="flex justify-center pt-8">
          <button
            type="button"
            onClick={onLoadMore}
            className="btn-ghost px-8 py-3"
          >
            {t('load_more')}
          </button>
        </div>
      )}
    </div>
  );
}
