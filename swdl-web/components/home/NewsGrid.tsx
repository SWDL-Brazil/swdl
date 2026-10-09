'use client';

import { useEffect, useState } from 'react';
import { useTranslations, useLocale } from 'next-intl';
import { motion } from 'motion/react';
import { api, resolveAssetUrl, News } from '@/lib/api';
import { Badge, CommitteeDot } from '@/components/ui/Badge';
import { Card, CardImage } from '@/components/ui/Card';
import { truncate } from '@/lib/utils';
import { formatTimeAgo, categoryLabelKey } from '@/lib/format';
import { ArrowRight } from 'lucide-react';
import Link from 'next/link';

const categoryColors: Record<string, 'crise' | 'oficial' | 'imprensa' | 'votacao'> = {
  crise: 'crise',
  oficial: 'oficial',
  imprensa: 'imprensa',
  votacao: 'votacao',
};

export function NewsGrid() {
  const t = useTranslations('home');
  const tn = useTranslations('noticias');
  const locale = useLocale();
  const [news, setNews] = useState<News[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadNews() {
      const data = await api.noticias({ limit: 3 });
      if (data) {
        setNews(data);
      }
      setLoading(false);
    }
    loadNews();
  }, []);

  if (loading) {
    return (
      <section className="py-20 bg-surface">
        <div className="container">
          <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-gold border-t-transparent rounded-full animate-spin" />
          </div>
        </div>
      </section>
    );
  }

  if (news.length === 0) return null;

  return (
    <section className="py-20 bg-surface">
      <div className="container">
        <div className="flex items-end justify-between mb-10">
          <div>
            <span className="section-label">{t('news_label')}</span>
            <h2 className="section-title">{t('news_title')}</h2>
          </div>
          <Link
            href="/noticias"
            className="hidden md:flex items-center gap-2 text-[#7a5f1f] text-sm font-medium hover:text-[#4a380c] transition-colors no-underline"
          >
            {t('news_all')} <ArrowRight size={16} />
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {news.map((item, i) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.6, delay: i * 0.1 }}
            >
              <Card className="h-full flex flex-col overflow-hidden">
                <CardImage
                  src={resolveAssetUrl(item.image_url)}
                  alt={item.title}
                  className="w-full h-48 -m-6 mb-0 rounded-t-lg"
                  fallback={<span className="text-5xl">📰</span>}
                />
                <div className="flex-1 flex flex-col p-6">
                  <div className="flex items-center gap-2 mb-3">
                    {item.committee && <CommitteeDot committee={item.committee} />}
                    <Badge variant={categoryColors[item.category_slug] || 'default'}>
                      {categoryLabelKey(item.category_slug)
                        ? tn(categoryLabelKey(item.category_slug)!)
                        : item.category}
                    </Badge>
                    <span className="text-xs text-slate">
                      {formatTimeAgo(item.created_at, locale, item.time_ago)}
                    </span>
                  </div>
                  <h3 className="font-display text-lg font-bold text-navy mb-2 line-clamp-2">
                    {item.title}
                  </h3>
                  {i === 0 && item.body && (
                    <p className="text-sm text-slate leading-relaxed mb-4 line-clamp-3">
                      {truncate(item.body, 150)}
                    </p>
                  )}
                  <div className="mt-auto">
                    <Link
                      href={`/noticia/${item.slug}`}
                      className="text-[#7a5f1f] text-sm font-medium hover:text-[#4a380c] transition-colors no-underline flex items-center gap-1"
                    >
                      {t('news_read')} <ArrowRight size={14} />
                    </Link>
                  </div>
                </div>
              </Card>
            </motion.div>
          ))}
        </div>

        <Link
          href="/noticias"
          className="md:hidden flex items-center justify-center gap-2 text-[#7a5f1f] text-sm font-medium hover:text-[#4a380c] transition-colors no-underline mt-8"
        >
          {t('news_all')} <ArrowRight size={16} />
        </Link>
      </div>
    </section>
  );
}
