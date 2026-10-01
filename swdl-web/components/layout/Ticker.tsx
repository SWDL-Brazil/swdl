'use client';

import { useEffect, useMemo, useState } from 'react';
import { useTranslations } from 'next-intl';
import { api, TickerItem } from '@/lib/api';

export function Ticker() {
  const t = useTranslations('ticker');
  const [raw, setRaw] = useState<TickerItem[]>([]);

  useEffect(() => {
    async function loadTicker() {
      const data = await api.ticker();
      if (data && data.length > 0) {
        setRaw(data);
      }
    }
    loadTicker();
    const interval = setInterval(loadTicker, 60000);
    return () => clearInterval(interval);
  }, []);

  const items = useMemo(() => {
    if (raw.length === 0) return [];
    const sorted = [...raw].sort((a, b) => {
      const ua = a.type === 'urgent' ? 1 : 0;
      const ub = b.type === 'urgent' ? 1 : 0;
      if (ua !== ub) return ub - ua;
      return (b.priority || 0) - (a.priority || 0);
    });
    return [...sorted, ...sorted];
  }, [raw]);

  const urgentCount = useMemo(
    () => raw.filter((i) => i.type === 'urgent').length,
    [raw]
  );

  if (items.length === 0) return null;

  return (
    <div className="bg-navy-dark border-b border-white/5 overflow-hidden h-10 flex items-center relative">
      <div className="bg-gold text-navy font-mono text-[0.72rem] font-bold tracking-[0.12em] uppercase px-5 h-full flex items-center shrink-0 z-10 whitespace-nowrap">
        {urgentCount > 0 ? `🚨 ${t('alerts', { n: urgentCount })}` : t('live')}
      </div>
      <div className="overflow-hidden flex-1 relative">
        <div className="animate-ticker flex items-center gap-8 whitespace-nowrap px-4">
          {items.map((item, i) => (
            <span
              key={i}
              className="text-slate-light text-xs flex items-center gap-2"
              dangerouslySetInnerHTML={{ __html: item.html }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
