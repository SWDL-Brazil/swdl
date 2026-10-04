'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import dynamic from 'next/dynamic';

const Globe3D = dynamic(
  () => import('@/components/home/Globe3D').then((mod) => mod.Globe3D),
  { ssr: false },
);

function Counter({ to }: { to: number }) {
  const [n, setN] = useState(0);
  useEffect(() => {
    let raf = 0;
    const start = performance.now();
    const tick = () => {
      const p = Math.min(1, (performance.now() - start) / 800);
      setN(Math.round(to * (1 - Math.pow(1 - p, 3))));
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [to]);
  return <>{n}</>;
}

export function SplashLoader() {
  const t = useTranslations('splash');
  const th = useTranslations('home');
  const [visible, setVisible] = useState(false);
  const [leaving, setLeaving] = useState(false);
  const [awake, setAwake] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [final, setFinal] = useState(false);

  useEffect(() => {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    try {
      if (sessionStorage.getItem('swdl-splash') === '1') return;
      sessionStorage.setItem('swdl-splash', '1');
    } catch {}
    setVisible(true);
    if (reduced) {
      const a = window.setTimeout(() => setLeaving(true), 500);
      const b = window.setTimeout(() => setVisible(false), 1200);
      return () => {
        window.clearTimeout(a);
        window.clearTimeout(b);
      };
    }
    const awakeT = window.setTimeout(() => setAwake(true), 1400);
    const statsT = window.setTimeout(() => {
      setShowStats(true);
      setFinal(true);
    }, 4400);
    const leaveT = window.setTimeout(() => setLeaving(true), 4900);
    const hideT = window.setTimeout(() => setVisible(false), 5650);
    return () => {
      window.clearTimeout(awakeT);
      window.clearTimeout(statsT);
      window.clearTimeout(leaveT);
      window.clearTimeout(hideT);
    };
  }, []);

  if (!visible) return null;

  return (
    <div
      aria-hidden="true"
      className={`fixed inset-0 z-[9999] bg-[#0D1B2A] transition-opacity duration-700 ${
        leaving ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}
    >
      <div className="splash-vignette" />
      <div className="max-w-6xl mx-auto h-full grid grid-cols-1 lg:grid-cols-2 items-center gap-10 px-8 md:px-14">
        <div className="relative z-10 py-20 lg:py-0">
          <p className="splash-brand">SWDL</p>
          <p className="splash-league">SESI World Diplomacy League</p>

          <p className="splash-establish">{t('establishing')}</p>
          <div className="splash-line" />

          <div className="mt-10 space-y-1.5">
            <p className="splash-word" style={{ animationDelay: '3.4s' }}>
              {th('hero_title_line1')}
            </p>
            <p className="splash-word gold" style={{ animationDelay: '3.75s' }}>
              {th('hero_title_line2')}
            </p>
            <p className="splash-word" style={{ animationDelay: '4.1s' }}>
              {th('hero_title_line3')}
            </p>
          </div>

          {showStats && (
            <div className="splash-stats">
              {[
                { to: 8, label: th('hero_stat_temas') },
                { to: 216, label: th('hero_stat_delegados') },
                { to: 193, label: th('hero_stat_paises') },
              ].map((s) => (
                <div key={s.label}>
                  <span className="block text-4xl font-display font-bold text-white">
                    <Counter to={s.to} />
                  </span>
                  <span className="text-xs text-slate-light">{s.label}</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className={`splash-globe-wrap ${awake ? 'awake' : ''} ${final ? 'final' : ''} hidden sm:block`}>
          <Globe3D />
        </div>
      </div>
    </div>
  );
}
