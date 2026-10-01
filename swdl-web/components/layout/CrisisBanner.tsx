'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { X } from 'lucide-react';
import { api, CrisisStatus } from '@/lib/api';

export function CrisisBanner() {
  const t = useTranslations('crisis_banner');
  const [status, setStatus] = useState<CrisisStatus | null>(null);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    async function checkStatus() {
      const data = await api.status();
      if (data) {
        setStatus(data);
        if (data.crisis_active) {
          setDismissed(false);
        }
      }
    }

    checkStatus();
    const interval = setInterval(checkStatus, 60000);
    return () => clearInterval(interval);
  }, []);

  if (!status?.crisis_active || dismissed || !status.crisis_message) return null;

  return (
    <div className="fixed top-[68px] left-0 right-0 z-[100] bg-red-700 py-2.5 px-6 flex items-center gap-3.5 animate-slide-down">
      <span className="w-2.5 h-2.5 rounded-full bg-white animate-pulse-slow shrink-0" />
      <span className="text-white text-sm font-medium flex-1">
        <strong className="text-red-100">{t('label')}</strong> {status.crisis_message}
      </span>
      <button
        onClick={() => setDismissed(true)}
        className="text-white/60 hover:text-white bg-transparent border-none cursor-pointer text-lg leading-none p-1 shrink-0 transition-colors"
        aria-label={t('close_aria')}
      >
        <X size={18} />
      </button>
    </div>
  );
}
