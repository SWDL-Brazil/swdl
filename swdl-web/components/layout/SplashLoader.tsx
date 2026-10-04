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

  useEffect(() => {
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    try {
      if (sessionStorage.getItem('swdl-splash') === '1') {
        (window as unknown as { __swdlSplashDone: boolean }).__swdlSplashDone = true;
        window.dispatchEvent(new Event('swdl-splash-done'));
        return;
      }
      sessionStorage.setItem('swdl-splash', '1');
    } catch {}
    setVisible(true);

    const done = () => {
      (window as unknown as { __swdlSplashDone: boolean }).__swdlSplashDone = true;
      window.dispatchEvent(new Event('swdl-splash-done'));
    };

    if (reduced) {
      const a = window.setTimeout(() => setLeaving(true), 500);
      const c = window.setTimeout(() => {
        setVisible(false);
        done();
      }, 1200);
      return () => {
        window.clearTimeout(a);
        window.clearTimeout(c);
      };
    }
    const awakeT = window.setTimeout(() => setAwake(true), 1400);
    const statsT = window.setTimeout(() => setShowStats(true), 4400);
    const leaveT = window.setTimeout(() => setLeaving(true), 4900);
    const hideT = window.setTimeout(() => {
      setVisible(false);
      done();
    }, 5650);
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

      <img
        src="/img/Logo/LOGO.svg"
        alt="SWDL"
        className="absolute top-6 left-6 md:top-8 md:left-16 w-16 z-10 opacity-0"
        style={{ animation: 'splash-fade 0.8s 0.4s ease forwards' }}
      />

      <div className="min-h-screen grid grid-cols-1 lg:grid-cols-2">
        {/* Left: same geometry/classes as Hero left column */}
        <div className="bg-navy flex flex-col justify-center px-8 md:px-16 py-24 lg:py-32 relative overflow-hidden">
          <div className="relative z-10">
            {/* spacer matching hero tag badge */}
            <div className="inline-flex items-center opacity-0 border border-gold/30 px-3.5 py-1.5 rounded-sm mb-7 text-[0.72rem] tracking-[0.14em]">
              &nbsp;
            </div>

            <div className="font-display text-[clamp(44px,5vw,74px)] font-black leading-[0.98] text-white mb-2.5">
              <p className="splash-word" style={{ animationDelay: '3.4s' }}>
                {th('hero_title_line1')}
              </p>
              <em className="not-italic text-gold block splash-word-em" style={{ animationDelay: '3.75s' }}>
                {th('hero_title_line2')}
              </em>
              <p className="splash-word" style={{ animationDelay: '4.1s' }}>
                {th('hero_title_line3')}
              </p>
            </div>

            {/* spacer matching hero subtitle */}
            <p className="max-w-[400px] my-5 opacity-0 text-base leading-relaxed">
              &nbsp;
            </p>

            {/* spacer matching hero buttons */}
            <div className="flex gap-3 opacity-0 h-[44px]">
              <span className="px-6 py-3">&nbsp;</span>
              <span className="px-6 py-3">&nbsp;</span>
            </div>

            {/* stats at end */}
            <div className="splash-stats !mt-10">
              {showStats ? (
                [
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
                ))
              ) : (
                <>
                  <div>
                    <span className="block text-4xl font-display font-bold text-white/0">0</span>
                    <span className="text-xs text-slate-light/0">&nbsp;</span>
                  </div>
                  <div>
                    <span className="block text-4xl font-display font-bold text-white/0">0</span>
                    <span className="text-xs text-slate-light/0">&nbsp;</span>
                  </div>
                  <div>
                    <span className="block text-4xl font-display font-bold text-white/0">0</span>
                    <span className="text-xs text-slate-light/0">&nbsp;</span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* setup overlay: brand + establishing */}
          <div className="splash-setup absolute inset-0 flex flex-col justify-center px-8 md:px-16 z-20 bg-navy">
            <p className="splash-brand">SWDL</p>
            <p className="splash-league">SESI World Diplomacy League</p>
            <p className="splash-establish">{t('establishing')}</p>
            <div className="splash-line" />
          </div>
        </div>

        {/* Right: identical geometry to Hero right column */}
        <div className="bg-navy relative hidden lg:flex items-center justify-center">
          <div className={`splash-globe-wrap ${awake ? 'awake' : ''} w-full h-full`}>
            <Globe3D />
          </div>
        </div>
      </div>
    </div>
  );
}
