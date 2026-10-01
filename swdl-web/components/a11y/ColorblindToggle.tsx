'use client';

import { useCallback, useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';

const STORAGE_KEY = 'swdl-cvd';

function readCvd(): boolean {
  if (typeof window === 'undefined') return false;
  try {
    return window.localStorage.getItem(STORAGE_KEY) === '1';
  } catch {
    return false;
  }
}

function applyCvd(on: boolean) {
  if (typeof document === 'undefined') return;
  if (on) {
    document.documentElement.setAttribute('data-cvd', 'true');
  } else {
    document.documentElement.removeAttribute('data-cvd');
  }
}

export function ColorblindToggle() {
  const t = useTranslations('a11y');
  const [on, setOn] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const initial = readCvd();
    setOn(initial);
    applyCvd(initial);
    setReady(true);
  }, []);

  const toggle = useCallback(() => {
    setOn((prev) => {
      const next = !prev;
      applyCvd(next);
      try {
        window.localStorage.setItem(STORAGE_KEY, next ? '1' : '0');
      } catch {
        /* ignore */
      }
      return next;
    });
  }, []);

  if (!ready) {
    return (
      <span
        className="inline-flex items-center font-mono text-[0.72rem] tracking-[0.1em] uppercase px-3 py-2 border border-white/15 text-white/40 rounded-sm"
        aria-hidden="true"
      >
        {t('cvd_label')}
      </span>
    );
  }

  return (
    <button
      type="button"
      onClick={toggle}
      aria-pressed={on}
      className={`inline-flex items-center gap-2 font-mono text-[0.72rem] tracking-[0.1em] uppercase px-3 py-2 rounded-sm border transition-colors cursor-pointer ${
        on
          ? 'bg-gold/20 border-gold/60 text-white'
          : 'bg-transparent border-white/25 text-slate-light hover:border-white/50 hover:text-white'
      }`}
    >
      <span aria-hidden="true" className="text-base leading-none">
        {on ? '●' : '○'}
      </span>
      {t('cvd_label')}
      <span className="sr-only">{on ? t('cvd_on') : t('cvd_off')}</span>
    </button>
  );
}
