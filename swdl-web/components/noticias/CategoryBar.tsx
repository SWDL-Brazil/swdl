'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { Search, ChevronLeft, ChevronRight } from 'lucide-react';
import type { Category } from '@/lib/api';
import { cn } from '@/lib/utils';

interface CategoryBarProps {
  categories: Category[];
  committees: string[];
  query: string;
  onQueryChange: (v: string) => void;
}

function ScrollRow({
  label,
  children,
  className,
}: {
  label: string;
  children: React.ReactNode;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [edge, setEdge] = useState({ left: false, right: false });

  const update = () => {
    const el = ref.current;
    if (!el) return;
    const left = el.scrollLeft > 4;
    const right = el.scrollLeft + el.clientWidth < el.scrollWidth - 4;
    setEdge({ left, right });
  };

  useEffect(() => {
    update();
    const el = ref.current;
    if (!el) return;
    const ro = new ResizeObserver(update);
    ro.observe(el);
    el.addEventListener('scroll', update, { passive: true });
    return () => {
      ro.disconnect();
      el.removeEventListener('scroll', update);
    };
  }, [children]);

  const scrollBy = (dir: 1 | -1) => {
    ref.current?.scrollBy({ left: dir * 200, behavior: 'smooth' });
  };

  return (
    <div className={cn('relative flex items-center min-w-0 w-full', className)}>
      <button
        type="button"
        aria-label={`Rolar ${label} para a esquerda`}
        onClick={() => scrollBy(-1)}
        className={cn(
          'absolute left-0 z-10 h-full w-8 items-center justify-center bg-gradient-to-r from-white via-white/90 to-transparent text-navy/70 hover:text-navy transition-opacity',
          edge.left ? 'flex' : 'hidden'
        )}
      >
        <ChevronLeft size={18} strokeWidth={2.2} />
      </button>

      <div
        ref={ref}
        className="flex items-center gap-1 overflow-x-auto min-w-0 w-full py-2 [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
        role="list"
      >
        {children}
      </div>

      <button
        type="button"
        aria-label={`Rolar ${label} para a direita`}
        onClick={() => scrollBy(1)}
        className={cn(
          'absolute right-0 z-10 h-full w-8 items-center justify-center bg-gradient-to-l from-white via-white/90 to-transparent text-navy/70 hover:text-navy transition-opacity',
          edge.right ? 'flex' : 'hidden'
        )}
      >
        <ChevronRight size={18} strokeWidth={2.2} />
      </button>
    </div>
  );
}

export function CategoryBar({
  categories,
  committees,
  query,
  onQueryChange,
}: CategoryBarProps) {
  const t = useTranslations('noticias');
  const router = useRouter();
  const searchParams = useSearchParams();

  const activeCat = searchParams.get('cat') || '';
  const activeCommittee = searchParams.get('committee') || '';

  const setParam = (key: string, value: string) => {
    const params = new URLSearchParams(searchParams.toString());
    if (value) params.set(key, value);
    else params.delete(key);
    router.push(`?${params.toString()}`, { scroll: false });
  };

  const KNOWN_CATS = ['geral', 'oficial', 'imprensa', 'crise', 'votacao'];
  const catTabs = useMemo(
    () => [
      { slug: '', name: t('category_all') },
      ...categories.map((c) => ({
        slug: c.slug,
        name: KNOWN_CATS.includes(c.slug) ? t(`category_${c.slug}`) : c.name,
      })),
    ],
    [categories, t]
  );

  const committeeTabs = useMemo(
    () => [
      { slug: '', name: t('all_committees') },
      ...committees.map((name) => ({ slug: name, name })),
    ],
    [committees, t]
  );

  const tabClass = (active: boolean) =>
    cn(
      'px-4 py-3 text-[13px] font-medium uppercase tracking-[0.08em] whitespace-nowrap rounded-sm border-b-2 transition-colors shrink-0 min-h-[44px]',
      active
        ? 'border-gold text-navy bg-surface-alt'
        : 'border-transparent text-slate hover:text-navy hover:bg-surface-alt/60'
    );

  return (
    <div className="bg-white border-b border-navy/10 sticky top-[68px] z-30 shadow-[0_1px_0_rgba(13,27,42,0.04)]">
      <div className="container-portal">
        <div className="flex flex-col lg:flex-row lg:items-stretch min-h-[56px]">
          {/* 1) Categorias */}
          <div className="flex items-center min-w-0 lg:flex-1 lg:pr-3 py-1">
            <ScrollRow label="categorias" className="w-full">
              {catTabs.map((tab) => (
                <button
                  key={tab.slug || 'all'}
                  onClick={() => setParam('cat', tab.slug)}
                  className={tabClass(activeCat === tab.slug)}
                  type="button"
                >
                  {tab.name}
                </button>
              ))}
            </ScrollRow>
          </div>

          {/* 2) Comitês / temas */}
          {committeeTabs.length > 1 && (
            <div className="flex items-center min-w-0 border-t border-navy/10 lg:border-t-0 lg:border-l lg:border-navy/10 lg:px-1 py-1 lg:max-w-[48%]">
              <ScrollRow label="comitês" className="w-full">
                {committeeTabs.map((tab) => (
                  <button
                    key={tab.slug || 'all-comm'}
                    onClick={() => setParam('committee', tab.slug)}
                    className={tabClass(activeCommittee === tab.slug)}
                    type="button"
                    title={tab.name}
                  >
                    {tab.name.length > 28 ? `${tab.name.slice(0, 28)}…` : tab.name}
                  </button>
                ))}
              </ScrollRow>
            </div>
          )}

          {/* 3) Busca */}
          <div className="relative flex items-center w-full lg:w-[200px] lg:shrink-0 border-t border-navy/10 lg:border-t-0 lg:ml-2 lg:pl-3 lg:border-l lg:border-navy/10 py-1">
            <Search size={15} className="absolute left-0 lg:left-3 text-slate pointer-events-none" />
            <input
              type="search"
              value={query}
              onChange={(e) => onQueryChange(e.target.value)}
              placeholder={t('search_placeholder')}
              className="w-full bg-transparent border-b-2 border-navy/15 pl-7 lg:pl-8 pr-2 py-3.5 text-sm text-navy placeholder:text-slate focus:outline-none focus:border-gold transition-colors"
              aria-label={t('search_placeholder')}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
