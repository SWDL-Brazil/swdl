'use client';

import { useEffect, useState } from 'react';

export function SplashLoader() {
  const [visible, setVisible] = useState(false);
  const [leaving, setLeaving] = useState(false);

  useEffect(() => {
    try {
      if (sessionStorage.getItem('swdl-splash') === '1') return;
      sessionStorage.setItem('swdl-splash', '1');
    } catch {}
    setVisible(true);
    const leave = window.setTimeout(() => setLeaving(true), 1300);
    const hide = window.setTimeout(() => setVisible(false), 1900);
    return () => {
      window.clearTimeout(leave);
      window.clearTimeout(hide);
    };
  }, []);

  if (!visible) return null;

  return (
    <div
      aria-hidden="true"
      className={`fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-[#0D1B2A] transition-opacity duration-500 ${
        leaving ? 'opacity-0 pointer-events-none' : 'opacity-100'
      }`}
    >
      <div className="splash-logo-wrap">
        <img src="/img/logo.svg" alt="SWDL" className="splash-logo" />
      </div>
      <div className="splash-line" />
      <p className="splash-tag">SESI World Diplomacy League</p>
    </div>
  );
}
