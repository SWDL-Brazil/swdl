'use client';

import { useTranslations } from 'next-intl';
import { motion } from 'motion/react';
import { Container } from '@/components/ui/Container';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

const galleryItems = [
  { icon: '/icons/scales.svg', key: 'g1', event: 'SWDL 2025' },
  { icon: '/icons/globe.svg', key: 'g2', event: 'SWDL 2025' },
  { icon: '/icons/handshake.svg', key: 'g3', event: 'SWDL 2025' },
  { icon: '/icons/trophy.svg', key: 'g4', event: 'SWDL 2025' },
  { icon: '/icons/microphone.svg', key: 'g5', event: 'SWDL 2025' },
] as const;

export function GalleryStrip() {
  const t = useTranslations('home');
  const ti = useTranslations('home.gallery_items');

  return (
    <section className="py-20 bg-navy">
      <Container>
        <div className="flex items-end justify-between mb-12">
          <div>
            <span className="section-label">
              <span className="w-7 h-px bg-gold" />
              {t('gallery_archive_label')}
            </span>
            <h2 className="section-title text-white">{t('gallery_editions_title')}</h2>
          </div>
        </div>

        <div className="space-y-4">
          {galleryItems.map((item, i) => (
            <motion.div
              key={item.key}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className="bg-navy-mid/50 border border-white/5 rounded-lg p-5 flex items-center gap-5 hover:bg-navy-mid transition-all duration-300 group"
            >
              <img src={item.icon} alt="" className="w-8 h-8 opacity-70" />
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <h3 className="font-medium text-white group-hover:text-gold transition-colors">{ti(`${item.key}.title`)}</h3>
                  <span className="text-xs font-mono text-gold/60">{item.event}</span>
                </div>
                <p className="text-sm text-slate-light line-clamp-1">{ti(`${item.key}.desc`)}</p>
              </div>
              <ArrowRight size={18} className="text-white/20 group-hover:text-gold transition-colors shrink-0" />
            </motion.div>
          ))}
        </div>
      </Container>
    </section>
  );
}
