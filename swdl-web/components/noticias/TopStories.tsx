import { NewsCard, type NewsLike } from './NewsCard';

interface TopStoriesProps {
  items: NewsLike[];
}

export function TopStories({ items }: TopStoriesProps) {
  if (items.length === 0) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 pt-8">
      {items.map((item) => (
        <NewsCard
          key={item.slug}
          item={item}
          imageHeight="md"
          showExcerpt
          className="pb-6 border-b border-navy/10"
        />
      ))}
    </div>
  );
}
