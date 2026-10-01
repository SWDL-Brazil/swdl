import { NewsCard, type NewsLike } from './NewsCard';

interface HeroSidebarProps {
  featured: NewsLike | null;
  list: NewsLike[];
}

export function HeroSidebar({ featured, list }: HeroSidebarProps) {
  if (!featured && list.length === 0) return null;

  return (
    <aside className="flex flex-col gap-5 h-full">
      {featured && (
        <NewsCard
          item={featured}
          imageHeight="md"
          className="pb-5 border-b border-navy/10"
        />
      )}

      {list.length > 0 && (
        <ul className="flex flex-col divide-y divide-navy/10 list-none p-0 m-0">
          {list.map((item) => (
            <li key={item.slug} className="py-1">
              <NewsCard item={item} imageHeight="sm" layout="horizontal" />
            </li>
          ))}
        </ul>
      )}
    </aside>
  );
}
