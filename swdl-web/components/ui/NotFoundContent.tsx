'use client';

import { useTranslations } from 'next-intl';
import { Container } from '@/components/ui/Container';
import { LinkButton } from '@/components/ui/Button';

export function NotFoundContent() {
  const t = useTranslations('page_404');

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface">
      <Container>
        <div className="text-center py-16">
          <div className="text-8xl mb-6">🌍</div>
          <h1 className="font-display text-4xl font-bold text-navy mb-4">
            {t('title')}
          </h1>
          <p className="text-slate text-lg mb-8">
            {t('subtitle')}
          </p>
          <LinkButton href="/" variant="primary">
            {t('back')}
          </LinkButton>
        </div>
      </Container>
    </div>
  );
}
