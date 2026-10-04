'use client';

import { useEffect, useRef, useState } from 'react';

export function SplashLoader() {
  const [visible, setVisible] = useState(false);
  const [leaving, setLeaving] = useState(false);
  const logoRef = useRef<HTMLDivElement>(null);
  const glowRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    try {
      if (sessionStorage.getItem('swdl-splash') === '1') return;
      sessionStorage.setItem('swdl-splash', '1');
    } catch {}
    setVisible(true);
    const leave = window.setTimeout(() => setLeaving(true), 2000);
    const hide = window.setTimeout(() => setVisible(false), 2650);
    return () => {
      window.clearTimeout(leave);
      window.clearTimeout(hide);
    };
  }, []);

  useEffect(() => {
    if (!visible) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    let tx = 0, ty = 0, cx = 0, cy = 0, raf = 0;
    const onMove = (e: MouseEvent) => {
      tx = (e.clientX / window.innerWidth - 0.5) * 2;
      ty = (e.clientY / window.innerHeight - 0.5) * 2;
    };
    const loop = () => {
      cx += (tx - cx) * 0.08;
      cy += (ty - cy) * 0.08;
      if (logoRef.current)
        logoRef.current.style.transform = `translate3d(${cx * 10}px, ${cy * 8}px, 0)`;
      if (glowRef.current)
        glowRef.current.style.transform = `translate3d(${cx * -18}px, ${cy * -14}px, 0)`;
      raf = requestAnimationFrame(loop);
    };
    window.addEventListener('mousemove', onMove);
    raf = requestAnimationFrame(loop);
    return () => {
      window.removeEventListener('mousemove', onMove);
      cancelAnimationFrame(raf);
    };
  }, [visible]);

  if (!visible) return null;

  return (
    <div
      aria-hidden="true"
      className={`fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-[#0D1B2A] transition-opacity duration-700 ${
        leaving ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}
    >
      <div className="splash-vignette" />
      <div ref={glowRef} className="splash-glow" />
      <div ref={logoRef} className="splash-logo-wrap">
        <div className="splash-logo-zoom">
          <img src="/img/Logo/LOGO.svg" alt="SWDL" className="splash-logo" />
        </div>
      </div>
      <div className="splash-line" />
      <p className="splash-tag">SESI World Diplomacy League</p>
    </div>
  );
}
