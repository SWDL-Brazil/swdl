'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { useLocale, useTranslations } from 'next-intl';
import Link from 'next/link';
import { Container } from '@/components/ui/Container';
import { api, BACKEND_ORIGIN, type CertificateLookup } from '@/lib/api';
import {
  ArrowLeft,
  FileDown,
  Loader2,
  Search,
  ShieldAlert,
  ShieldCheck,
} from 'lucide-react';

type Phase = 'idle' | 'loading' | 'valid' | 'not_found' | 'error' | 'empty';

function formatDate(iso: string | null, locale: string): string {
  if (!iso) return '';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return '';
  try {
    return d.toLocaleDateString(locale, {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    });
  } catch {
    return '';
  }
}

export function CertificadoContent() {
  const t = useTranslations('certificado');
  const tc = useTranslations('common');
  const locale = useLocale();
  const searchParams = useSearchParams();
  const [code, setCode] = useState('');
  const [phase, setPhase] = useState<Phase>('idle');
  const [result, setResult] = useState<CertificateLookup | null>(null);

  const lookup = async (raw: string) => {
    const value = raw.trim();
    if (!value) {
      setPhase('empty');
      setResult(null);
      return;
    }
    setPhase('loading');
    setResult(null);
    const res = await api.certificado(value);
    setResult(res);
    setPhase(res.status === 'valid' ? 'valid' : res.status);
  };

  useEffect(() => {
    const q = searchParams.get('code');
    if (q) {
      setCode(q);
      void lookup(q);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const reset = () => {
    setPhase('idle');
    setResult(null);
    setCode('');
  };

  const data = result?.status === 'valid' ? result.data : null;
  const showResult = phase === 'valid' || phase === 'not_found' || phase === 'error';

  return (
    <div className="pt-[68px]">
      {/* Hero */}
      <section className="bg-navy py-14 md:py-16 relative overflow-hidden">
        <div
          aria-hidden
          className="absolute inset-0 flex items-center justify-center pointer-events-none select-none"
        >
          <span className="font-display text-[48px] md:text-[110px] font-black text-white/[0.03] uppercase">
            {t('watermark')}
          </span>
        </div>
        <Container className="relative z-10">
          <div className="flex items-center gap-2 text-slate-light text-sm mb-4">
            <Link href="/" className="hover:text-white transition-colors">
              {tc('home')}
            </Link>
            <span>›</span>
            <span className="text-white">{t('hero_title')}</span>
          </div>
          <span className="section-label">
            <span className="w-7 h-px bg-gold" />
            {t('hero_label')}
          </span>
          <h1 className="font-display text-[clamp(32px,4vw,52px)] font-bold text-white mb-3">
            {t('hero_title')}
          </h1>
          <p className="text-slate-light text-base max-w-2xl">{t('hero_desc')}</p>
        </Container>
      </section>

      {/* Form + resultado */}
      <section className="py-12 md:py-16 bg-white">
        <Container>
          <div className="max-w-xl mx-auto">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                void lookup(code);
              }}
              className="rounded-xl border border-navy/8 bg-surface p-6 md:p-8"
            >
              <label
                htmlFor="cert-code"
                className="block font-mono text-[0.72rem] tracking-widest uppercase text-navy/70 mb-2"
              >
                {t('input_label')}
              </label>
              <div className="flex flex-col sm:flex-row gap-3">
                <input
                  id="cert-code"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder={t('placeholder')}
                  autoComplete="off"
                  spellCheck={false}
                  className="flex-1 min-w-0 px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all font-mono uppercase bg-white"
                />
                <button
                  type="submit"
                  disabled={phase === 'loading'}
                  className="btn-primary justify-center px-6 py-3 inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {phase === 'loading' ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Search size={16} />
                  )}
                  {phase === 'loading' ? t('checking') : t('submit')}
                </button>
              </div>
              <p className="mt-3 text-xs text-navy/50">{t('hint')}</p>
              {phase === 'empty' && (
                <p className="mt-2 text-sm text-red-700">{t('empty_error')}</p>
              )}
            </form>

            {/* Válido */}
            {phase === 'valid' && data && (
              <div className="mt-6 rounded-xl border border-emerald-600/30 bg-emerald-50/70 p-6 md:p-8">
                <div className="flex items-center gap-3 mb-5">
                  <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-white">
                    <ShieldCheck size={20} />
                  </span>
                  <div className="min-w-0">
                    <div className="font-mono text-[0.68rem] tracking-[0.1em] uppercase text-emerald-700">
                      {t('valid_badge')}
                    </div>
                    <div className="font-display text-lg md:text-xl font-bold text-navy">
                      {t('valid_title')}
                    </div>
                  </div>
                </div>

                <div className="rounded-lg bg-white border border-navy/8 p-5">
                  <div className="font-mono text-[0.68rem] tracking-[0.1em] uppercase text-navy/50 mb-1">
                    {t('participant_label')}
                  </div>
                  <div className="font-display text-2xl font-bold text-navy break-words mb-5">
                    {data.name}
                  </div>

                  <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {(data.country || data.country_flag) && (
                      <div>
                        <dt className="font-mono text-[0.66rem] tracking-widest uppercase text-navy/45">
                          {t('country_label')}
                        </dt>
                        <dd className="text-sm text-navy font-medium">
                          {data.country_flag} {data.country}
                        </dd>
                      </div>
                    )}
                    {(data.committee || data.committee_name) && (
                      <div>
                        <dt className="font-mono text-[0.66rem] tracking-widest uppercase text-navy/45">
                          {t('committee_label')}
                        </dt>
                        <dd className="text-sm text-navy font-medium break-words">
                          {data.committee && <strong>{data.committee}</strong>}
                          {data.committee && data.committee_name && ' — '}
                          {data.committee_name}
                        </dd>
                      </div>
                    )}
                    <div>
                      <dt className="font-mono text-[0.66rem] tracking-widest uppercase text-navy/45">
                        {t('code_label')}
                      </dt>
                      <dd className="text-sm text-navy font-mono break-all">
                        {data.verification_code}
                      </dd>
                    </div>
                    {data.global_id && (
                      <div>
                        <dt className="font-mono text-[0.66rem] tracking-widest uppercase text-navy/45">
                          {t('global_id_label')}
                        </dt>
                        <dd className="text-xs text-navy/70 font-mono break-all">
                          {data.global_id}
                        </dd>
                      </div>
                    )}
                  </dl>
                </div>

                {data.digital_signature && (
                  <div className="mt-4 flex flex-wrap items-center gap-3">
                    <span className="inline-flex items-center gap-1.5 font-mono text-[0.68rem] tracking-[0.1em] uppercase px-2.5 py-1 rounded-sm bg-navy text-white">
                      <ShieldCheck size={12} />
                      {t('signed_badge')}
                    </span>
                    {data.signed_at && (
                      <span className="text-xs text-navy/60">
                        {t('signed_date')}: {formatDate(data.signed_at, locale)}
                      </span>
                    )}
                    {data.signature_valid === false && (
                      <span className="text-xs text-red-700 font-medium">
                        {t('signature_invalid')}
                      </span>
                    )}
                  </div>
                )}

                {data.pdf_path && (
                  <a
                    href={`${BACKEND_ORIGIN}${data.pdf_path}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-5 inline-flex items-center gap-2 btn-primary"
                  >
                    <FileDown size={16} />
                    {t('view_pdf')}
                  </a>
                )}
              </div>
            )}

            {/* Não encontrado */}
            {phase === 'not_found' && (
              <div className="mt-6 rounded-xl border border-red-600/25 bg-red-50/70 p-6">
                <div className="flex items-start gap-3">
                  <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-red-700 text-white mt-0.5">
                    <ShieldAlert size={18} />
                  </span>
                  <div>
                    <div className="font-display text-lg font-bold text-navy mb-1">
                      {t('not_found_title')}
                    </div>
                    <p className="text-sm text-navy/70 leading-relaxed">
                      {t('not_found_desc')}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Erro de rede */}
            {phase === 'error' && (
              <div className="mt-6 rounded-xl border border-amber-600/30 bg-amber-50/70 p-6">
                <div className="flex items-start gap-3">
                  <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-amber-600 text-white mt-0.5">
                    <ShieldAlert size={18} />
                  </span>
                  <p className="text-sm text-navy/80 leading-relaxed pt-1.5">
                    {t('network_error')}
                  </p>
                </div>
              </div>
            )}

            {showResult && (
              <button
                type="button"
                onClick={reset}
                className="mt-5 inline-flex items-center gap-2 text-sm text-slate hover:text-navy transition-colors bg-transparent border-none cursor-pointer p-0"
              >
                <ArrowLeft size={14} />
                {t('search_again')}
              </button>
            )}
          </div>
        </Container>
      </section>
    </div>
  );
}
