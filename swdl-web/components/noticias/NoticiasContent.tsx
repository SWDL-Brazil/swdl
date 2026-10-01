'use client';

import { Suspense, useEffect, useMemo, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { api, News, Category } from '@/lib/api';
import { CategoryBar } from './CategoryBar';
import { LeadStory } from './LeadStory';
import { TopStories } from './TopStories';
import { HeroSidebar } from './HeroSidebar';
import { CrisisFeed } from './CrisisFeed';
import { CommitteeSections } from './CommitteeSections';
import { ArchiveList } from './ArchiveList';
import { NewsSidebar } from './NewsSidebar';
import { type NewsLike } from './NewsCard';

const PAGE_SIZE = 8;

function PortalInner() {
  const t = useTranslations('noticias');
  const router = useRouter();
  const searchParams = useSearchParams();

  const [news, setNews] = useState<News[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [themeNames, setThemeNames] = useState<string[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

  const activeCat = searchParams.get('cat') || '';
  const activeCommittee = searchParams.get('committee') || '';

  useEffect(() => {
    async function loadData() {
      const [newsData, catsData, comitesData] = await Promise.all([
        api.noticias({ limit: 40 }),
        api.categorias(),
        api.comites(),
      ]);
      if (newsData) setNews(newsData);
      if (catsData) setCategories(catsData);
      if (comitesData) {
        setThemeNames(comitesData.map((c) => c.name).filter(Boolean));
      }
      setLoading(false);
    }
    loadData();
  }, []);

  // Abas curtas (CS, DHR…) vêm das notícias; temas longos só como fallback
  const committees = useMemo(() => {
    const fromNews = Array.from(
      new Set(
        news
          .map((n) => (n.committee || '').trim())
          .filter((c) => c && c.toLowerCase() !== 'geral')
      )
    );
    if (fromNews.length > 0) return fromNews;
    return themeNames.filter((n) => n.toLowerCase() !== 'geral');
  }, [news, themeNames]);

  const filtered = useMemo(() => {
    let list = [...news];
    if (activeCat) list = list.filter((n) => n.category_slug === activeCat);
    if (activeCommittee) list = list.filter((n) => n.committee === activeCommittee);
    if (query.trim()) {
      const q = query.trim().toLowerCase();
      list = list.filter((n) => n.title.toLowerCase().includes(q));
    }
    return list;
  }, [news, activeCat, activeCommittee, query]);

  const lead = filtered[0] || null;
  const top = filtered.slice(1, 4);
  const heroSideList = filtered.slice(4, 9);
  const heroSideFeatured = filtered[9] || null;
  const crises = news.filter((n) => n.is_crisis).slice(0, 4);
  const archive = filtered.slice(10, 10 + visibleCount);
  const hasMore = filtered.length > 10 + visibleCount;
  const trending = useMemo(
    () => [...news].sort((a, b) => b.id - a.id).slice(0, 5),
    [news]
  );

  const byCommittee = useMemo(() => {
    const map: Record<string, NewsLike[]> = {};
    for (const name of committees) {
      map[name] = news.filter((n) => n.committee === name);
    }
    return map;
  }, [news, committees]);

  const setCommittee = (name: string) => {
    const params = new URLSearchParams(searchParams.toString());
    if (name) params.set('committee', name);
    else params.delete('committee');
    router.push(`?${params.toString()}`, { scroll: false });
  };

  return (
    <div className="pt-[68px]">
      <CategoryBar
        categories={categories}
        committees={committees}
        query={query}
        onQueryChange={(v) => {
          setQuery(v);
          setVisibleCount(PAGE_SIZE);
        }}
      />

      {/* Page title */}
      <div className="container-portal pt-12 pb-6">
        <div className="section-rule">
          <div>
            <p className="news-kicker mb-2">SWDL</p>
            <h1 className="font-display text-[clamp(36px,5vw,56px)] font-bold text-navy leading-none m-0">
              {t('portal_title')}
            </h1>
          </div>
          <p className="news-meta m-0">
            {t('portal_count', { n: filtered.length })}
          </p>
        </div>
      </div>

      {loading ? (
        <div className="container-portal flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-gold border-t-transparent rounded-full animate-spin" />
        </div>
      ) : filtered.length === 0 ? (
        <div className="container-portal text-center py-16">
          <p className="text-slate text-lg">{t('empty')}</p>
        </div>
      ) : (
        <>
          {/* HERO 75/25 */}
          <section className="container-portal pb-4">
            <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] xl:grid-cols-[1fr_360px] gap-8 lg:gap-10">
              <div className="min-w-0">
                {lead && <LeadStory item={lead} />}
                <TopStories items={top as NewsLike[]} />
              </div>
              <div className="min-w-0">
                <div className="hidden lg:block">
                  <HeroSidebar
                    featured={heroSideFeatured as NewsLike | null}
                    list={heroSideList as NewsLike[]}
                  />
                </div>
              </div>
            </div>
          </section>

          {/* AO VIVO */}
          <div className="container-portal">
            <CrisisFeed items={crises as NewsLike[]} />
          </div>

          {/* POR COMITÊ */}
          <div className="container-portal">
            <CommitteeSections
              committees={committees}
              active={activeCommittee}
              byCommittee={byCommittee}
              onSelect={setCommittee}
            />
          </div>

          {/* ARQUIVO + SIDEBAR */}
          <section className="container-portal py-10">
            <div className="section-rule mb-6">
              <h2>{t('section_archive')}</h2>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] xl:grid-cols-[1fr_340px] gap-10">
              <div className="min-w-0">
                <ArchiveList
                  items={archive as NewsLike[]}
                  hasMore={hasMore}
                  onLoadMore={() => setVisibleCount((c) => c + PAGE_SIZE)}
                />
              </div>
              <div className="hidden lg:block">
                <NewsSidebar trending={trending as NewsLike[]} />
              </div>
            </div>
          </section>
        </>
      )}
    </div>
  );
}

export function NoticiasContent() {
  const t = useTranslations('noticias');
  return (
    <Suspense
      fallback={
        <div className="pt-[68px] container-portal flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-gold border-t-transparent rounded-full animate-spin" />
          <span className="sr-only">{t('portal_title')}</span>
        </div>
      }
    >
      <PortalInner />
    </Suspense>
  );
}
