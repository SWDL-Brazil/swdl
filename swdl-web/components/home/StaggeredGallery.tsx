'use client';

import { useTranslations } from 'next-intl';
import { motion } from 'motion/react';
import { Container } from '@/components/ui/Container';

interface GalleryImage {
  src: string;
  altKey: string;
  captionKey: string;
  offset: string;
}

const images: GalleryImage[] = [
  {
    src: '/img/equipe/Julia_3.png',
    altKey: 'staggered.0.alt',
    captionKey: 'staggered.0.caption',
    offset: '',
  },
  {
    src: '/img/world.jpg',
    altKey: 'staggered.1.alt',
    captionKey: 'staggered.1.caption',
    offset: 'md:mt-12',
  },
  {
    src: '/img/equipe/MAFRA.png',
    altKey: 'staggered.2.alt',
    captionKey: 'staggered.2.caption',
    offset: 'md:mt-24',
  },
];

export function StaggeredGallery() {
  const t = useTranslations('home');

  return (
    <section className="pb-20 bg-surface">
      <Container>
        {/* Header */}
        <div className="mb-10">
          <motion.span
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5 }}
            className="section-label"
          >
            <span className="w-7 h-px bg-gold" />
            {t('gallery_label')}
          </motion.span>
          <motion.h2
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.08 }}
            className="section-title"
          >
            {t('gallery_title')}
          </motion.h2>
        </div>

        {/* Staggered 12-col grid */}
        <div className="grid items-start gap-6 md:grid-cols-12 md:gap-6">
          {images.map((img, i) => (
            <motion.figure
              key={i}
              initial={{ opacity: 0, y: 22 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-60px' }}
              transition={{ duration: 0.6, delay: i * 0.12 }}
              className={`group relative overflow-hidden rounded-2xl ring-1 ring-navy/10 md:col-span-4 ${img.offset}`}
            >
              {/* Image with zoom hover */}
              <div className="overflow-hidden">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={img.src}
                  alt={t(img.altKey)}
                  loading="lazy"
                  decoding="async"
                  className="photo w-full object-cover aspect-[4/5] transition-transform duration-700 ease-out group-hover:scale-105"
                  style={{ objectPosition: '50% 50%' }}
                />
              </div>

              {/* Bottom gradient overlay */}
              <span
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 bg-gradient-to-t from-navy/70 via-navy/5 to-transparent opacity-80"
              />

              {/* Caption */}
              <figcaption className="absolute inset-x-0 bottom-0 p-5 text-[0.66rem] uppercase leading-relaxed tracking-[0.18em] text-white/85">
                {t(img.captionKey)}
              </figcaption>
            </motion.figure>
          ))}
        </div>
      </Container>
    </section>
  );
}
