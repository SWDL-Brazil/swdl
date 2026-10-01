'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';

interface CountdownProps {
  targetTime: string;
}

function pad(n: number): string {
  return String(Math.max(0, n)).padStart(2, '0');
}

function diffToTarget(targetTime: string): number {
  if (!targetTime) return 0;
  const [th, tm] = targetTime.split(':').map(Number);
  if (Number.isNaN(th) || Number.isNaN(tm)) return 0;
  const now = new Date();
  const target = new Date(now);
  target.setHours(th, tm, 0, 0);
  return Math.max(0, Math.floor((target.getTime() - now.getTime()) / 1000));
}

export function Countdown({ targetTime }: CountdownProps) {
  const t = useTranslations('agenda');
  const [seconds, setSeconds] = useState<number | null>(null);

  useEffect(() => {
    setSeconds(diffToTarget(targetTime));
    const id = setInterval(() => {
      setSeconds(diffToTarget(targetTime));
    }, 1000);
    return () => clearInterval(id);
  }, [targetTime]);

  if (seconds === null) {
    return (
      <div className="flex gap-1 justify-end lg:justify-end">
        <div className="bg-white/7 rounded px-2.5 py-1.5 text-center min-w-[52px]">
          <span className="block font-display text-xl font-bold text-white leading-none">--</span>
          <span className="block font-mono text-[0.62rem] tracking-[0.1em] uppercase text-slate-light mt-0.5">
            {t('countdown_min')}
          </span>
        </div>
        <div className="bg-white/7 rounded px-2.5 py-1.5 text-center min-w-[52px]">
          <span className="block font-display text-xl font-bold text-white leading-none">--</span>
          <span className="block font-mono text-[0.62rem] tracking-[0.1em] uppercase text-slate-light mt-0.5">
            {t('countdown_seg')}
          </span>
        </div>
      </div>
    );
  }

  const min = Math.floor(seconds / 60);
  const sec = seconds % 60;

  return (
    <div className="flex gap-1 justify-start lg:justify-end">
      <div className="bg-white/7 rounded px-2.5 py-1.5 text-center min-w-[52px]">
        <span className="block font-display text-xl font-bold text-white leading-none">{pad(min)}</span>
        <span className="block font-mono text-[0.62rem] tracking-[0.1em] uppercase text-slate-light mt-0.5">
          {t('countdown_min')}
        </span>
      </div>
      <div className="bg-white/7 rounded px-2.5 py-1.5 text-center min-w-[52px]">
        <span className="block font-display text-xl font-bold text-white leading-none">{pad(sec)}</span>
        <span className="block font-mono text-[0.62rem] tracking-[0.1em] uppercase text-slate-light mt-0.5">
          {t('countdown_seg')}
        </span>
      </div>
    </div>
  );
}
