import { notFound } from 'next/navigation';
import Link from 'next/link';
import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import { api, resolveAssetUrl, News } from '@/lib/api';
import { NewsMeta, NewsCard, type NewsLike } from '@/components/noticias/NewsCard';
import { formatTimeAgo, categoryLabelKey } from '@/lib/format';

interface Props {
  params: { locale: string; slug: string };
}

async function getNews(slug: string): Promise<News | null> {
  return api.noticia(slug);
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const news = await getNews(params.slug);
  if (!news) {
    try {
      const t = await getTranslations('meta');
      return { title: t('noticia_title') };
    } catch {
      return { title: 'Notícia — SWDL' };
    }
  }
  return {
    title: `${news.title} — SWDL`,
    description: news.excerpt || news.title,
    openGraph: {
      title: news.title,
      description: news.excerpt || news.title,
      images: news.image_url ? [resolveAssetUrl(news.image_url)] : undefined,
    },
  };
}

export default async function NoticiaPage({ params }: Props) {
  const news = await getNews(params.slug);
  if (!news || !news.body) notFound();

  const t = await getTranslations('noticia');
  const tn = await getTranslations('noticias');
  const tc = await getTranslations('common');
  const related = (news.related || []) as NewsLike[];
  const body = news.body;
  const excerpt = news.excerpt || '';
  const tags = news.tags || [];
  const catKey = categoryLabelKey(news.category_slug);
  const created = news.created_at
    ? new Date(news.created_at).toLocaleDateString(params.locale, {
        day: '2-digit',
        month: 'long',
        year: 'numeric',
      })
    : formatTimeAgo(news.created_at, params.locale, news.time_ago);

  return (
    <div className="pt-[68px]">
      {/* Kicker + title */}
      <header className="container-portal pt-12 pb-8">
        <Link
          href="/noticias"
          className="news-kicker inline-flex items-center gap-2 mb-6 no-underline hover:text-gold-dark transition-colors"
        >
          ← {t('back_portal')}
        </Link>

        <div className="max-w-[900px]">
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <span className="news-kicker">{catKey ? tn(catKey) : news.category}</span>
            {news.is_crisis && (
              <span className="inline-flex items-center gap-1.5 font-mono text-[0.72rem] font-bold uppercase tracking-[0.12em] text-[#9a3412]">
                <span className="w-1.5 h-1.5 rounded-full bg-[#9a3412] animate-pulse" />
                {tc('live')}
              </span>
            )}
          </div>

          <h1 className="font-display text-[clamp(32px,4.5vw,48px)] font-bold text-navy leading-[1.12] mb-5">
            {news.title}
          </h1>

          <div className="flex flex-wrap items-center gap-3 pb-6 border-b border-navy/10">
            <NewsMeta item={news} showBadge={false} />
            <span className="meta-sep">|</span>
            <span className="news-meta">{news.author || 'SWDL'}</span>
            <span className="meta-sep">|</span>
            <span className="news-meta">{created}</span>
          </div>
        </div>
      </header>

      {/* Hero image */}
      {news.image_url && (
        <div className="container-portal mb-10">
          <div className="overflow-hidden rounded-sm bg-surface-alt">
            <img
              src={resolveAssetUrl(news.image_url)}
              alt={news.title}
              className="w-full h-[min(540px,50vw)] object-cover"
              loading="eager"
            />
          </div>
        </div>
      )}

      {/* Body + sidebar */}
      <div className="container-portal pb-20">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_300px] xl:grid-cols-[1fr_340px] gap-10 lg:gap-14">
          <article className="min-w-0 max-w-[900px]">
            {excerpt && (
              <p className="text-lg leading-relaxed text-slate italic mb-8 pb-8 border-b border-navy/10">
                {excerpt}
              </p>
            )}

            <div className="article-body" dangerouslySetInnerHTML={{ __html: body }} />

            {tags.length > 0 && (
              <div className="mt-10 pt-8 border-t border-navy/10">
                <p className="news-kicker mb-3">{t('tags')}</p>
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag) => (
                    <span
                      key={tag}
                      className="font-mono text-[0.72rem] font-semibold uppercase tracking-[0.08em] px-3 py-1.5 rounded-sm bg-navy/5 border border-navy/10 text-navy"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {related.length > 0 && (
              <section className="mt-12 pt-8 border-t-4 border-navy">
                <div className="section-rule border-t-0 pt-0 mb-6">
                  <h2 className="text-[24px]">{t('related')}</h2>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  {related.map((item) => (
                    <NewsCard
                      key={item.slug}
                      item={item}
                      imageHeight="sm"
                      layout="horizontal"
                      className="p-4 bg-white border border-navy/10 rounded-sm"
                    />
                  ))}
                </div>
              </section>
            )}
          </article>

          <aside className="hidden lg:block">
            <div className="sticky top-[140px] bg-white rounded-sm border border-navy/10 p-5">
              <p className="news-kicker mb-4 pb-3 border-b border-navy/10 m-0">
                {t('sidebar_title')}
              </p>
              <ul className="list-none p-0 m-0 flex flex-col gap-4">
                {related.slice(0, 5).map((item, i) => (
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
                        {formatTimeAgo(item.created_at, params.locale, item.time_ago) && (
                          <span className="news-meta mt-1 block">
                            {formatTimeAgo(item.created_at, params.locale, item.time_ago)}
                          </span>
                        )}
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
