'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { motion } from 'motion/react';
import { Container } from '@/components/ui/Container';
import { LinkButton } from '@/components/ui/Button';
import { Clock, ArrowRight } from 'lucide-react';

const DEADLINE = new Date('2026-09-30T23:59:00-03:00');

function useCountdown(target: Date) {
  const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0, expired: false });

  useEffect(() => {
    function calc() {
      const diff = Math.max(0, target.getTime() - Date.now());
      if (diff === 0) return { days: 0, hours: 0, minutes: 0, seconds: 0, expired: true };
      return {
        days: Math.floor(diff / 86400000),
        hours: Math.floor((diff % 86400000) / 3600000),
        minutes: Math.floor((diff % 3600000) / 60000),
        seconds: Math.floor((diff % 60000) / 1000),
        expired: false,
      };
    }
    setTimeLeft(calc());
    const interval = setInterval(() => setTimeLeft(calc()), 1000);
    return () => clearInterval(interval);
  }, [target]);

  return timeLeft;
}

export function InscricoesCountdown() {
  const t = useTranslations('home');
  const { days, hours, minutes, seconds, expired } = useCountdown(DEADLINE);

  return (
    <section className="py-12 bg-surface">
      <Container>
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="bg-white rounded-xl border border-navy/5 p-8 md:p-10 shadow-card"
        >
          <div className="flex flex-col md:flex-row items-center gap-8">
            {/* Left - Theme */}
            <div className="flex-1 text-center md:text-left">
              <span className="section-label justify-center md:justify-start">
                <span className="w-7 h-px bg-gold" />
                {t('next_debate_label')}
              </span>
              <h3 className="font-display text-2xl md:text-3xl font-bold text-navy mb-2">
                {t('next_debate_title')}
              </h3>
              <p className="text-slate text-lg">{t('next_debate_theme')}</p>
              <p className="text-sm text-slate mt-3">{t('closes_in')}</p>
            </div>

            {/* Right - Countdown */}
            <div className="flex items-center gap-4">
              {expired ? (
                <div className="text-center">
                  <span className="text-red-700 font-bold text-lg">{t('registrations_closed')}</span>
                </div>
              ) : (
                <>
                  <CountdownUnit value={days} label={t('unit_days')} />
                  <span className="text-2xl font-bold text-navy/30">:</span>
                  <CountdownUnit value={hours} label={t('unit_hours')} />
                  <span className="text-2xl font-bold text-navy/30">:</span>
                  <CountdownUnit value={minutes} label={t('countdown_min')} />
                  <span className="text-2xl font-bold text-navy/30">:</span>
                  <CountdownUnit value={seconds} label={t('countdown_seg')} />
                </>
              )}
            </div>
          </div>

          {/* CTA */}
          <div className="mt-8 text-center">
            <LinkButton href="/faca-parte" variant="primary">
              {t('cta_register')} <ArrowRight size={16} />
            </LinkButton>
          </div>
        </motion.div>
      </Container>
    </section>
  );
}

function CountdownUnit({ value, label }: { value: number; label: string }) {
  return (
    <div className="text-center">
      <div className="bg-navy text-white rounded-lg w-16 h-16 md:w-20 md:h-20 flex items-center justify-center">
        <span className="font-display text-3xl md:text-4xl font-bold">
          {String(value).padStart(2, '0')}
        </span>
      </div>
      <span className="text-xs text-slate mt-2 block">{label}</span>
    </div>
  );
}
