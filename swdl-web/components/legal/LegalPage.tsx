'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { Container } from '@/components/ui/Container';
import Link from 'next/link';
import { ArrowLeft, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';

type LegalNamespace = 'termos' | 'privacidade' | 'aviso_legal';

interface LegalSection {
  title: string;
  body: string;
}

interface LegalPageProps {
  namespace: LegalNamespace;
}

function sectionId(index: number) {
  return `sec-${index + 1}`;
}

function stripNumber(title: string) {
  return title.replace(/^\d+\.\s*/, '');
}

export function LegalPage({ namespace }: LegalPageProps) {
  const t = useTranslations(namespace);
  const tc = useTranslations('common');
  const tl = useTranslations('legal');
  const sections = (t.raw('sections') as LegalSection[]) || [];
  const [active, setActive] = useState(0);

  useEffect(() => {
    const els = sections.map((_, i) => document.getElementById(sectionId(i))).filter(Boolean) as HTMLElement[];
    if (!els.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);
        if (visible[0]) {
          const idx = els.findIndex((el) => el.id === visible[0].target.id);
          if (idx >= 0) setActive(idx);
        }
      },
      { rootMargin: '-100px 0px -55% 0px', threshold: [0, 0.25, 0.5] }
    );

    els.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [sections.length]);

  return (
    <div className="pt-[68px]">
      {/* Hero */}
      <section className="bg-navy py-14 md:py-16 relative overflow-hidden">
        <div
          aria-hidden
          className="absolute inset-0 flex items-center justify-center pointer-events-none select-none"
        >
          <span className="font-display text-[72px] md:text-[140px] font-black text-white/[0.03]">
            LEGAL
          </span>
        </div>
        <Container className="relative z-10">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-slate-light text-sm hover:text-white transition-colors no-underline mb-5"
          >
            <ArrowLeft size={16} /> {tc('back')}
          </Link>
          <div className="flex items-center gap-2 text-slate-light text-sm mb-4">
            <Link href="/" className="hover:text-white transition-colors">
              {tc('home')}
            </Link>
            <span>›</span>
            <span className="text-white">{t('hero_title')}</span>
          </div>
          <span className="section-label">
            <span className="w-7 h-px bg-gold" />
            {tl('label')}
          </span>
          <h1 className="font-display text-[clamp(32px,4vw,52px)] font-bold text-white mb-3">
            {t('hero_title')}
          </h1>
          <p className="text-slate-light text-base max-w-2xl">{t('content')}</p>
          <p className="mt-4 font-mono text-[0.75rem] tracking-widest uppercase text-white/70">
            {tl('updated')}: {t('updated_date')}
          </p>
        </Container>
      </section>

      {/* Body + TOC */}
      <section className="py-12 md:py-16 bg-white">
        <Container>
          <div className="grid grid-cols-1 lg:grid-cols-[240px_minmax(0,1fr)] gap-10 lg:gap-14 max-w-5xl mx-auto">
            {/* TOC */}
            <aside className="lg:sticky lg:top-[92px] lg:self-start">
              <div className="rounded-xl border border-navy/8 bg-surface p-4">
                <div className="flex items-center gap-2 mb-3">
                  <FileText size={14} className="text-[#7a5f1f]" />
                  <span className="font-mono text-[0.72rem] tracking-widest uppercase text-navy/70">
                    {tl('toc')}
                  </span>
                </div>
                <nav aria-label={tl('toc')}>
                  <ol className="list-none space-y-1">
                    {sections.map((s, i) => (
                      <li key={s.title}>
                        <a
                          href={`#${sectionId(i)}`}
                          className={cn(
                            'flex items-start gap-2 rounded-md px-2 py-1.5 text-[13px] leading-snug no-underline transition-colors',
                            active === i
                              ? 'bg-gold/10 text-navy font-medium'
                              : 'text-slate hover:text-navy hover:bg-navy/4'
                          )}
                        >
                          <span className="font-mono text-[0.72rem] text-[#7a5f1f] mt-0.5 shrink-0 w-4">
                            {String(i + 1).padStart(2, '0')}
                          </span>
                          <span className="line-clamp-2">{stripNumber(s.title)}</span>
                        </a>
                      </li>
                    ))}
                  </ol>
                </nav>
              </div>
            </aside>

            {/* Content */}
            <article className="min-w-0">
              <div className="max-w-[680px]">
                {sections.map((s, i) => (
                  <section
                    key={s.title}
                    id={sectionId(i)}
                    className="scroll-mt-28 mb-10 last:mb-0"
                  >
                    <h2 className="flex items-center gap-3 font-display text-xl md:text-[22px] font-bold text-navy mb-4 pb-3 border-b border-navy/10">
                      <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-gold text-navy font-mono text-[0.75rem] font-bold shrink-0">
                        {i + 1}
                      </span>
                      <span>{stripNumber(s.title)}</span>
                    </h2>
                    <p className="text-[15px] leading-[1.75] text-navy/85 mb-3 last:mb-0">
                      {s.body}
                    </p>
                  </section>
                ))}

                <div className="mt-12 pt-6 border-t border-navy/10">
                  <Link
                    href="/"
                    className="inline-flex items-center gap-2 text-sm text-slate hover:text-navy transition-colors no-underline"
                  >
                    <ArrowLeft size={16} /> {tc('back_home')}
                  </Link>
                </div>
              </div>
            </article>
          </div>
        </Container>
      </section>
    </div>
  );
}
