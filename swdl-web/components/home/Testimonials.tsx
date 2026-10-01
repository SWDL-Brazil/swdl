'use client';

import { useTranslations } from 'next-intl';
import { useState, useEffect, useCallback } from 'react';
import { motion } from 'motion/react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Container } from '@/components/ui/Container';

interface Testimonial {
  name: string;
  avatar: string;
  quoteKey: string;
  roleKey: string;
}

const testimonials: Testimonial[] = [
  {
    name: 'Ana Beatriz Silva',
    roleKey: 'testimonials_items.0.role',
    avatar: '/img/equipe/Eloisa.jpg',
    quoteKey: 'testimonials_items.0.quote',
  },
  {
    name: 'Lucas Ferreira',
    roleKey: 'testimonials_items.1.role',
    avatar: '/img/equipe/santiago.jpg',
    quoteKey: 'testimonials_items.1.quote',
  },
  {
    name: 'Mariana Costa',
    roleKey: 'testimonials_items.2.role',
    avatar: '/img/equipe/Talita.jpg',
    quoteKey: 'testimonials_items.2.quote',
  },
];

const AUTOPLAY_MS = 7000;

export function Testimonials() {
  const t = useTranslations('home');
  const tc = useTranslations('common');
  const [current, setCurrent] = useState(0);
  const total = testimonials.length;

  const goTo = useCallback(
    (idx: number) => {
      setCurrent(((idx % total) + total) % total);
    },
    [total]
  );

  const next = useCallback(() => goTo(current + 1), [current, goTo]);
  const prev = useCallback(() => goTo(current - 1), [current, goTo]);

  // Autoplay — setTimeout (sem re-render por frame)
  useEffect(() => {
    const id = setTimeout(() => setCurrent((c) => (c + 1) % total), AUTOPLAY_MS);
    return () => clearTimeout(id);
  }, [current, total]);

  return (
    <section className="py-20 bg-surface">
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
            {t('testimonials_label')}
          </motion.span>
          <motion.h2
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.08 }}
            className="section-title"
          >
            {t('testimonials_title')}
          </motion.h2>
        </div>

        {/* Carousel card */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="relative select-none"
        >
          <div
            role="region"
            aria-roledescription="carousel"
            aria-label={t('testimonials_label')}
            className="relative overflow-hidden rounded-[1.75rem] border border-navy/10 bg-white shadow-card"
          >
            {/* Top gold hairline */}
            <span
              aria-hidden="true"
              className="pointer-events-none absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-gold/70 to-transparent"
            />
            {/* Radial glow */}
            <span
              aria-hidden="true"
              className="pointer-events-none absolute inset-0 bg-[radial-gradient(60%_70%_at_12%_0%,rgba(201,168,76,0.08),transparent_72%)]"
            />

            {/* Slides track */}
            <div
              className="flex transition-transform duration-[900ms]"
              style={{
                transform: `translate3d(-${current * 100}%, 0, 0)`,
                transitionTimingFunction: 'cubic-bezier(0.22, 1, 0.36, 1)',
              }}
            >
              {testimonials.map((item, i) => (
                <figure
                  key={i}
                  aria-hidden={i !== current}
                  className="relative w-full shrink-0 px-7 py-12 md:px-16 md:py-20"
                >
                  {/* Decorative quote mark */}
                  <span
                    aria-hidden="true"
                    className="font-display text-6xl md:text-7xl leading-none text-gold/35"
                  >
                    &ldquo;
                  </span>

                  {/* Quote */}
                  <blockquote
                    className="mt-2 max-w-3xl font-display text-[1.5rem] leading-[1.28] tracking-[-0.015em] text-navy md:text-[2.1rem]"
                    style={{
                      opacity: i === current ? 1 : 0,
                      transform: i === current ? 'none' : 'translateY(10px)',
                      transition: 'opacity 700ms ease 120ms, transform 700ms ease 120ms',
                    }}
                  >
                    {t(item.quoteKey)}
                  </blockquote>

                  {/* Author */}
                  <figcaption className="mt-10 flex items-center gap-4">
                    <span className="relative block h-14 w-14 shrink-0 overflow-hidden rounded-full ring-1 ring-navy/10">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={item.avatar}
                        alt={item.name}
                        width={56}
                        height={56}
                        className="h-14 w-14 rounded-full object-cover"
                        style={{ objectPosition: '50% 50%' }}
                      />
                    </span>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-navy">{item.name}</p>
                      <p className="text-[0.68rem] uppercase tracking-[0.16em] text-slate">
                        {t(item.roleKey)}
                      </p>
                    </div>
                  </figcaption>
                </figure>
              ))}
            </div>
          </div>

          {/* Controls */}
          <div className="mt-7 flex items-center justify-between gap-6">
            {/* Progress bars */}
            <div className="flex items-center gap-2.5" role="tablist">
              {testimonials.map((_, i) => (
                <button
                  key={i}
                  type="button"
                  role="tab"
                  aria-label={`${t('testimonials_label')} ${i + 1}`}
                  aria-current={i === current}
                  onClick={() => goTo(i)}
                  className="group/bar -my-3 flex h-auto w-10 items-center py-3"
                >
                  <span className="relative block h-[2px] w-full overflow-hidden rounded-full bg-navy/10">
                    <span
                      className="absolute inset-y-0 left-0 bg-gold"
                      style={{
                        width:
                          i < current
                            ? '100%'
                            : i === current
                              ? '100%'
                              : '0%',
                        animation:
                          i === current
                            ? `progressFill ${AUTOPLAY_MS}ms linear forwards`
                            : undefined,
                      }}
                    />
                    <span className="absolute inset-0 opacity-0 transition-opacity duration-300 group-hover/bar:opacity-100 bg-gold/40" />
                  </span>
                </button>
              ))}
            </div>

            {/* Arrows */}
            <div className="flex items-center gap-2">
              <button
                type="button"
                aria-label={tc('prev')}
                onClick={prev}
                className="flex h-10 w-10 items-center justify-center rounded-full border border-navy/15 text-navy/70 transition-all duration-300 hover:-translate-y-0.5 hover:border-gold/45 hover:text-gold-dark"
              >
                <ChevronLeft size={16} />
              </button>
              <button
                type="button"
                aria-label={t('testimonials_next')}
                onClick={next}
                className="flex h-10 w-10 items-center justify-center rounded-full border border-navy/15 text-navy/70 transition-all duration-300 hover:-translate-y-0.5 hover:border-gold/45 hover:text-gold-dark"
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </motion.div>
      </Container>
    </section>
  );
}
