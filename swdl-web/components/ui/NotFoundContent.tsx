'use client';

import { useTranslations } from 'next-intl';
import { Container } from '@/components/ui/Container';
import { LinkButton } from '@/components/ui/Button';

export function NotFoundContent() {
  const t = useTranslations('page_404');

  return (
    <div className="flex items-center justify-center bg-surface py-24">
      <Container>
        <div className="text-center">
          <p className="font-mono text-[0.7rem] tracking-[0.3em] uppercase text-gold mb-4">
            {t('eyebrow')}
          </p>
          <h1 className="font-display text-7xl md:text-8xl font-bold text-navy leading-none mb-6">
            404
          </h1>
          <div className="w-12 h-px bg-gold mx-auto mb-6" />
          <h2 className="font-display text-2xl text-navy mb-3">{t('title')}</h2>
          <p className="text-slate text-base md:text-lg mb-10 max-w-md mx-auto">
            {t('subtitle')}
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <LinkButton href="/" variant="navy">
              {t('back')}
            </LinkButton>
            <LinkButton href="/comites" variant="ghost">
              {t('committees')}
            </LinkButton>
          </div>
        </div>
      </Container>
    </div>
  );
}
