'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import dynamic from 'next/dynamic';
import { LinkButton } from '@/components/ui/Button';
import { ArrowRight, Eye } from 'lucide-react';
import { motion } from 'motion/react';

function useSplashDone() {
  const [ready, setReady] = useState(false);
  useEffect(() => {
    if ((window as unknown as { __swdlSplashDone?: boolean }).__swdlSplashDone) {
      setReady(true);
      return;
    }
    const onDone = () => setReady(true);
    window.addEventListener('swdl-splash-done', onDone);
    return () => window.removeEventListener('swdl-splash-done', onDone);
  }, []);
  return ready;
}

const Globe3D = dynamic(() => import('./Globe3D').then(mod => mod.Globe3D), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full min-h-[400px] bg-navy-mid/30 rounded-full flex items-center justify-center">
      <div className="w-48 h-48 rounded-full border-2 border-gold/30 animate-spin-slow" />
    </div>
  ),
});

const stats = [
  { value: 8, labelKey: 'hero_stat_temas' },
  { value: 216, labelKey: 'hero_stat_delegados' },
  { value: 193, labelKey: 'hero_stat_paises' },
];

export function Hero() {
  const t = useTranslations('home');
  const ready = useSplashDone();

  const a = (delay: number) => ({
    initial: { opacity: 0, y: 20 },
    animate: ready ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 },
    transition: { duration: 0.6, delay },
  });

  return (
    <section className="min-h-screen grid grid-cols-1 lg:grid-cols-2 overflow-hidden relative">
      {/* Left content - extends full height including under navbar */}
      <div className="bg-navy flex flex-col justify-center px-8 md:px-16 py-24 lg:py-32 relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute w-[520px] h-[520px] -top-40 -left-40 rounded-full border border-gold/10" />
          <div className="absolute w-[300px] h-[300px] -bottom-16 right-24 rounded-full border border-gold/5" />
          <div className="absolute w-[160px] h-[160px] top-[55%] left-[65%] rounded-full border border-white/5" />
        </div>

        <div className="relative z-10">
          {/* Tag */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={ready ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="inline-flex items-center gap-2 font-mono text-[0.72rem] tracking-[0.14em] uppercase text-gold border border-gold/30 px-3.5 py-1.5 rounded-sm mb-7"
          >
            <span className="text-[7px]">◆</span>
            {t('hero_tag')}
          </motion.div>

          {/* Title */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={ready ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="font-display text-[clamp(44px,5vw,74px)] font-black leading-[0.98] text-white mb-2.5"
          >
            {t('hero_title_line1')}
            <em className="not-italic text-gold block">{t('hero_title_line2')}</em>
            {t('hero_title_line3')}
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={ready ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.6, delay: 0.35 }}
            className="text-base font-light leading-relaxed text-slate-light max-w-[400px] my-5"
          >
            {t('hero_sub')}
          </motion.p>

          {/* Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={ready ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.6, delay: 0.45 }}
            className="flex gap-3 flex-wrap"
          >
            <LinkButton href="/faca-parte" variant="primary">
              {t('hero_btn_parte')} <ArrowRight size={16} />
            </LinkButton>
            <LinkButton href="/comites" variant="ghost-white">
              <Eye size={16} /> {t('hero_btn_temas')}
            </LinkButton>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={ready ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
            transition={{ duration: 0.6, delay: 0.55 }}
            className="flex gap-10 mt-10"
          >
            {stats.map((stat) => (
              <div key={stat.value}>
                <span className="block text-4xl font-display font-bold text-white">
                  {stat.value}
                </span>
                <span className="text-xs text-slate-light">{t(stat.labelKey)}</span>
              </div>
            ))}
          </motion.div>
        </div>
      </div>

      {/* Right - Globe */}
      <div className="bg-navy relative hidden lg:flex items-center justify-center">
        <Globe3D />
      </div>
    </section>
  );
}
