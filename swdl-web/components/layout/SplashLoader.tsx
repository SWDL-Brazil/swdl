'use client';

import { useEffect, useRef, useState } from 'react';
import { useTranslations } from 'next-intl';

const CITIES: [number, number][] = [
  [-23.55, -46.63], // São Paulo
  [-22.91, -43.17], // Rio de Janeiro
  [-15.78, -47.93], // Brasília
  [40.71, -74.01], // New York
  [51.51, -0.13], // London
  [48.86, 2.35], // Paris
  [52.52, 13.41], // Berlin
  [55.76, 37.62], // Moscow
  [35.68, 139.69], // Tokyo
  [39.90, 116.4], // Beijing
  [28.61, 77.21], // New Delhi
  [25.2, 55.27], // Dubai
  [-33.87, 151.21], // Sydney
  [1.35, 103.82], // Singapore
  [19.43, -99.13], // Mexico City
  [-34.6, -58.38], // Buenos Aires
  [41.01, 28.98], // Istanbul
  [-1.29, 36.82], // Nairobi
  [30.04, 31.24], // Cairo
  [37.57, 126.98], // Seoul
  [13.76, 100.5], // Bangkok
  [-6.2, 106.85], // Jakarta
];

const ARCS: [number, number][] = [
  [0, 4], [0, 3], [3, 4], [4, 5], [8, 0], [8, 9], [2, 15], [14, 3], [0, 15], [10, 21], [17, 16], [12, 13],
];

function project(lat: number, lng: number, angle: number) {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lng + 180) * (Math.PI / 180);
  let x = -Math.sin(phi) * Math.cos(theta);
  const y = Math.cos(phi);
  const z0 = Math.sin(phi) * Math.sin(theta);
  const xr = x * Math.cos(angle) + z0 * Math.sin(angle);
  const zr = -x * Math.sin(angle) + z0 * Math.cos(angle);
  return { x: xr, y, z: zr };
}

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
  const canvasRef = useRef<HTMLCanvasElement>(null);

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

  useEffect(() => {
    if (!visible) return;
    const canvas = canvasRef.current;
    if (!canvas) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    let raf = 0;
    const t0 = performance.now();

    const draw = (now: number) => {
      const elapsed = now - t0;
      const dpr = window.devicePixelRatio || 1;
      const size = canvas.clientWidth;
      if (canvas.width !== size * dpr) {
        canvas.width = size * dpr;
        canvas.height = size * dpr;
      }
      const ctx = canvas.getContext('2d');
      if (!ctx) return;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, size, size);

      const cx = size / 2;
      const cy = size / 2;
      const R = size * 0.38;
      const angle = elapsed * 0.00022;

      // faint sphere outline
      ctx.beginPath();
      ctx.arc(cx, cy, R, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(201,168,76,0.12)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // points (staggered appearance over first ~2s)
      const pts = CITIES.map(([lat, lng], i) => {
        const appear = elapsed > 200 + i * 70;
        const p = project(lat, lng, angle);
        return { ...p, appear };
      });

      for (const p of pts) {
        if (!p.appear || p.z < 0.05) continue;
        const alpha = 0.25 + p.z * 0.75;
        ctx.beginPath();
        ctx.arc(cx + p.x * R, cy - p.y * R, 1.6 + p.z * 1.4, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(201,168,76,${alpha})`;
        ctx.fill();
      }

      // arcs after ~1.6s
      const arcsOn = elapsed > 1600;
      for (let i = 0; i < ARCS.length; i++) {
        const [a, b] = ARCS[i];
        const start = 1600 + i * 220;
        if (!arcsOn || elapsed < start) continue;
        const p = Math.min(1, (elapsed - start) / 900);
        const pa = pts[a];
        const pb = pts[b];
        if (pa.z <= 0 || pb.z <= 0) continue;
        const ax = cx + pa.x * R;
        const ay = cy - pa.y * R;
        const bx = cx + pb.x * R;
        const by = cy - pb.y * R;
        const mx = (ax + bx) / 2;
        const my = (ay + by) / 2;
        const dx = mx - cx;
        const dy = my - cy;
        const len = Math.hypot(dx, dy) || 1;
        const lift = R * 0.28;
        const qx = mx + (dx / len) * lift;
        const qy = my + (dy / len) * lift;
        ctx.beginPath();
        ctx.moveTo(ax, ay);
        ctx.quadraticCurveTo(qx, qy, ax + (bx - ax) * p, ay + (by - ay) * p);
        ctx.strokeStyle = `rgba(201,168,76,${0.35 * p})`;
        ctx.lineWidth = 0.8;
        ctx.stroke();
      }

      raf = requestAnimationFrame(draw);
    };

    raf = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(raf);
  }, [visible]);

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
          <canvas ref={canvasRef} className="splash-globe-canvas" />
        </div>
      </div>
    </div>
  );
}
