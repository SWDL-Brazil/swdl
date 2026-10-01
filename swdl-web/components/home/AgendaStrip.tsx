'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { motion } from 'motion/react';
import { api, AgendaItem } from '@/lib/api';
import { formatTime } from '@/lib/utils';
import { Clock, MapPin } from 'lucide-react';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

export function AgendaStrip() {
  const t = useTranslations('home');
  const tc = useTranslations('common');
  const [items, setItems] = useState<AgendaItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAgenda() {
      const data = await api.agenda({ limit: 5 });
      if (data) {
        setItems(data);
      }
      setLoading(false);
    }
    loadAgenda();
  }, []);

  if (loading) {
    return (
      <section className="py-20 bg-white">
        <div className="container">
          <div className="flex items-center justify-center h-48">
            <div className="w-8 h-8 border-2 border-gold border-t-transparent rounded-full animate-spin" />
          </div>
        </div>
      </section>
    );
  }

  if (items.length === 0) return null;

  return (
    <section className="py-20 bg-white">
      <div className="container">
        <div className="flex items-end justify-between mb-10">
          <div>
            <span className="section-label">{t('agenda_label')}</span>
            <h2 className="section-title">{t('agenda_title')}</h2>
          </div>
          <Link
            href="/agenda"
            className="hidden md:flex items-center gap-2 text-[#7a5f1f] text-sm font-medium hover:text-[#4a380c] transition-colors no-underline"
          >
            {t('agenda_full')} <ArrowRight size={16} />
          </Link>
        </div>

        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-4 top-0 bottom-0 w-px bg-gold/20 hidden md:block" />

          <div className="space-y-4">
            {items.map((item, i) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true, margin: '-50px' }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className={`relative flex items-start gap-4 p-4 rounded-lg transition-all duration-300 ${
                  item.status === 'now'
                    ? 'bg-gold/10 border border-gold/30'
                    : 'bg-surface hover:bg-surface-alt'
                }`}
              >
                {/* Time */}
                <div className="flex items-center gap-2 text-sm font-mono text-navy w-24 shrink-0">
                  <Clock size={14} className="text-[#7a5f1f]" />
                  <span>{formatTime(item.start_time)}</span>
                  {item.end_time && (
                    <span className="text-slate">— {formatTime(item.end_time)}</span>
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    {item.status === 'now' && (
                      <span className="bg-gold text-navy text-[0.72rem] font-bold px-2 py-0.5 rounded uppercase tracking-wider">
                        {tc('now')}
                      </span>
                    )}
                    <h3 className="font-medium text-navy truncate">{item.title}</h3>
                  </div>
                  {item.description && (
                    <p className="text-sm text-slate line-clamp-1">{item.description}</p>
                  )}
                  {item.location && (
                    <div className="flex items-center gap-1 mt-1 text-xs text-slate">
                      <MapPin size={12} />
                      {item.location}
                    </div>
                  )}
                </div>

                {/* Committee badge */}
                {item.committee && (
                  <span className="text-xs font-mono text-slate bg-navy/5 px-2 py-1 rounded shrink-0">
                    {item.committee}
                  </span>
                )}
              </motion.div>
            ))}
          </div>
        </div>

        <Link
          href="/agenda"
          className="md:hidden flex items-center justify-center gap-2 text-[#7a5f1f] text-sm font-medium hover:text-[#4a380c] transition-colors no-underline mt-8"
        >
          {t('agenda_full')} <ArrowRight size={16} />
        </Link>
      </div>
    </section>
  );
}
