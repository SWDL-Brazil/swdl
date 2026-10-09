'use client';

import { useEffect, useMemo, useState } from 'react';
import { useMessages, useTranslations } from 'next-intl';
import { AnimatePresence, motion } from 'motion/react';
import { api, CommitteeStatus } from '@/lib/api';
import { committeeColorVar } from '@/lib/committee-colors';
import { Container } from '@/components/ui/Container';
import Link from 'next/link';
import { ChevronRight, Download } from 'lucide-react';

type Section = 'themes' | 'committees' | 'manual';

interface CommitteeEntry {
  id: string;
  number: string;
  section: Section;
  code: string;
  metaKey: string;
  titleKey: string;
  orgKey?: string;
  descriptionKey: string;
  topicsKey?: string;
  delegatesKey?: string;
  color: string;
  icon: string;
  guide?: string;
  manual?: string;
}

const MANUAL_PDF = '/PDF/Manual Oficial dos Delegados (5).pdf';
const CS_PDF = '/PDF/Conselho de Segurança das Nações Unidas.pdf';
const ACNUR_PDF = '/PDF/Guia de Comitê - ACNUR.pdf';
const MISOGINIA_PDF =
  '/PDF/Misoginia como Violação dos Direitos Humanos Ações e Responsabilidades Internacionais.pdf';

const committees: CommitteeEntry[] = [
  {
    id: 'escravidao',
    number: '01',
    section: 'themes',
    code: 'ESCRAVIDÃO',
    metaKey: 'edition_2026',
    titleKey: 'entries.escravidao.title',
    descriptionKey: 'entries.escravidao.description',
    topicsKey: 'entries.escravidao.topics',
    delegatesKey: 'entries.escravidao.delegates',
    color: committeeColorVar('escravidao'),
    icon: '/icons/handshake.svg',
  },
  {
    id: 'acnur',
    number: '02',
    section: 'themes',
    code: 'ACNUR',
    metaKey: 'edition_2026',
    titleKey: 'entries.acnur.title',
    descriptionKey: 'entries.acnur.description',
    topicsKey: 'entries.acnur.topics',
    delegatesKey: 'entries.acnur.delegates',
    color: committeeColorVar('acnur'),
    icon: '/icons/dove.svg',
    guide: ACNUR_PDF,
    manual: MANUAL_PDF,
  },
  {
    id: 'ormuz',
    number: '03',
    section: 'themes',
    code: 'ORMUZ',
    metaKey: 'edition_2026',
    titleKey: 'entries.ormuz.title',
    descriptionKey: 'entries.ormuz.description',
    topicsKey: 'entries.ormuz.topics',
    delegatesKey: 'entries.ormuz.delegates',
    color: committeeColorVar('ormuz'),
    icon: '/icons/atom.svg',
    guide: CS_PDF,
    manual: MANUAL_PDF,
  },
  {
    id: 'canabis',
    number: '04',
    section: 'themes',
    code: 'CANÁBIS',
    metaKey: 'edition_2025',
    titleKey: 'entries.canabis.title',
    descriptionKey: 'entries.canabis.description',
    topicsKey: 'entries.canabis.topics',
    delegatesKey: 'entries.canabis.delegates',
    color: committeeColorVar('canabis'),
    icon: '/icons/leaf.svg',
  },
  {
    id: 'misoginia',
    number: '05',
    section: 'themes',
    code: 'MISOGINIA',
    metaKey: 'edition_2025',
    titleKey: 'entries.misoginia.title',
    descriptionKey: 'entries.misoginia.description',
    topicsKey: 'entries.misoginia.topics',
    delegatesKey: 'entries.misoginia.delegates',
    color: committeeColorVar('misoginia'),
    icon: '/icons/scales.svg',
    guide: MISOGINIA_PDF,
  },
  {
    id: 'mma',
    number: '06',
    section: 'committees',
    code: 'MMA',
    metaKey: 'meta_mma',
    titleKey: 'entries.mma.title',
    descriptionKey: 'entries.mma.description',
    topicsKey: 'entries.mma.topics',
    delegatesKey: 'entries.mma.delegates',
    color: committeeColorVar('mma'),
    icon: '/icons/leaf.svg',
  },
  {
    id: 'dhr',
    number: '07',
    section: 'committees',
    code: 'DHR',
    metaKey: 'meta_dhr',
    titleKey: 'entries.dhr.title',
    descriptionKey: 'entries.dhr.description',
    topicsKey: 'entries.dhr.topics',
    delegatesKey: 'entries.dhr.delegates',
    color: committeeColorVar('dhr'),
    icon: '/icons/scales.svg',
  },
  {
    id: 'ecosoc',
    number: '08',
    section: 'committees',
    code: 'ECOSOC',
    metaKey: 'meta_ecosoc',
    titleKey: 'entries.ecosoc.title',
    descriptionKey: 'entries.ecosoc.description',
    topicsKey: 'entries.ecosoc.topics',
    delegatesKey: 'entries.ecosoc.delegates',
    color: committeeColorVar('ecosoc'),
    icon: '/icons/coins.svg',
  },
  {
    id: 'disec',
    number: '09',
    section: 'committees',
    code: 'DISEC',
    metaKey: 'meta_disec',
    titleKey: 'entries.disec.title',
    descriptionKey: 'entries.disec.description',
    topicsKey: 'entries.disec.topics',
    delegatesKey: 'entries.disec.delegates',
    color: committeeColorVar('disec'),
    icon: '/icons/atom.svg',
  },
  {
    id: 'oms',
    number: '10',
    section: 'committees',
    code: 'OMS',
    metaKey: 'meta_oms',
    titleKey: 'entries.oms.title',
    descriptionKey: 'entries.oms.description',
    topicsKey: 'entries.oms.topics',
    delegatesKey: 'entries.oms.delegates',
    color: committeeColorVar('oms'),
    icon: '/icons/hospital.svg',
  },
  {
    id: 'cs',
    number: '11',
    section: 'committees',
    code: 'CS',
    metaKey: 'meta_cs',
    titleKey: 'entries.cs.title',
    descriptionKey: 'entries.cs.description',
    topicsKey: 'entries.cs.topics',
    delegatesKey: 'entries.cs.delegates',
    color: committeeColorVar('cs'),
    icon: '/icons/shield.svg',
    guide: CS_PDF,
  },
  {
    id: 'manual',
    number: '',
    section: 'manual',
    code: 'MANUAL',
    metaKey: 'edition_2026',
    titleKey: 'entries.manual.title',
    orgKey: 'entries.manual.org',
    descriptionKey: 'entries.manual.description',
    topicsKey: '',
    delegatesKey: '',
    color: committeeColorVar('manual'),
    icon: '/icons/graduation.svg',
    guide: MANUAL_PDF,
  },
];

function normalize(value: string): string {
  return value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

function matchStatus(entry: CommitteeEntry, apiCommittees: CommitteeStatus[]): CommitteeStatus | null {
  const entryKeys = [entry.code, entry.id]
    .map(normalize)
    .filter(Boolean);

  for (const api of apiCommittees) {
    const apiName = normalize(api.name);
    if (!apiName) continue;

    for (const key of entryKeys) {
      if (key.length >= 4 && (apiName.includes(key) || key.includes(apiName))) {
        return api;
      }
    }
  }

  return null;
}

function statusClass(type: string): string {
  const base = (() => {
    switch (type) {
      case 'voting':
        return 'bg-amber-50 text-amber-900 border-amber-400';
      case 'debate':
        return 'bg-emerald-50 text-emerald-900 border-emerald-500';
      case 'waiting':
        return 'bg-slate/10 text-slate-dark border-slate/40';
      default:
        return 'bg-navy/5 text-navy border-navy/20';
    }
  })();
  const cvd =
    type === 'voting'
      ? 'cvd-status-voting'
      : type === 'debate'
        ? 'cvd-status-debate'
        : type === 'waiting'
          ? 'cvd-status-waiting'
          : 'cvd-status-done';
  return `${base} cvd-chip ${cvd}`;
}

function SectionHeading({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-4 pt-10 pb-2 first:pt-0">
      <span className="font-mono text-[0.75rem] tracking-[0.2em] uppercase text-gold-dark">{label}</span>
      <span className="h-px flex-1 bg-navy/10" />
    </div>
  );
}

function CommitteeRow({
  entry,
  status,
  isOpen,
  onToggle,
  delay,
}: {
  entry: CommitteeEntry;
  status?: CommitteeStatus | null;
  isOpen: boolean;
  onToggle: () => void;
  delay: number;
}) {
  const tc = useTranslations('comites');
  const allMessages = useMessages() as Record<string, unknown>;
  const messages = (allMessages.comites ?? {}) as Record<string, unknown>;
  const hasDownloads = Boolean(entry.guide || entry.manual);
  const statusKey =
    status?.status_type &&
    ['voting', 'debate', 'waiting'].includes(status.status_type)
      ? `status_${status.status_type}`
      : null;
  const showStatus = status && status.status_type !== 'done';

  function resolveArray(path: string): string[] {
    const parts = path.split('.');
    let cur: unknown = messages;
    for (const p of parts) {
      if (cur == null || typeof cur !== 'object') return [];
      cur = (cur as Record<string, unknown>)[p];
    }
    return Array.isArray(cur) ? (cur as string[]) : [];
  }

  const topics = entry.topicsKey ? resolveArray(entry.topicsKey) : [];
  const delegates = entry.delegatesKey ? tc(entry.delegatesKey) : '';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-40px' }}
      transition={{ duration: 0.5, delay }}
      className="relative border-b border-navy/10"
    >
      <span
        aria-hidden="true"
        className="pointer-events-none absolute left-0 top-0 h-full w-[3px] origin-top transition-transform duration-700 ease-[cubic-bezier(0.22,1,0.36,1)] group-hover:scale-y-100 group-aria-expanded:scale-y-100"
        style={{
          backgroundColor: entry.color,
          transform: isOpen ? 'scaleY(1)' : undefined,
        }}
      />

      <div className="pl-5 pr-4 md:pl-8 md:pr-6">
        <button
          type="button"
          onClick={onToggle}
          aria-expanded={isOpen}
          className="group relative w-full -mx-2 px-2 text-left py-7 pr-8 md:-mx-3 md:px-3 md:py-8 md:pr-10 transition-colors duration-500 hover:bg-surface focus-visible:outline-none focus-visible:bg-surface"
        >
          <span
            aria-hidden="true"
            className="pointer-events-none absolute right-0 top-1/2 -translate-y-1/2 text-navy/30 transition-all duration-500 group-hover:text-navy/70"
          >
            <ChevronRight
              size={18}
              className={`transition-transform duration-500 ${isOpen ? 'rotate-90' : ''}`}
            />
          </span>

          <div className="flex items-start gap-3 md:grid md:grid-cols-12 md:gap-8">
            <span
              className={`relative shrink-0 font-mono text-[0.7rem] leading-none tracking-[0.22em] transition-colors duration-500 md:col-span-1 md:pt-[0.65rem] min-w-[1.75rem] ${entry.number ? '' : 'hidden md:block'}`}
              style={{ color: isOpen ? entry.color : undefined }}
            >
              <span className={isOpen ? '' : 'text-slate group-hover:text-navy'}>
                {entry.number}
              </span>
            </span>

            <div className="relative min-w-0 flex-1 md:col-span-11">
              <div className="flex flex-wrap items-center gap-2.5 mb-2">
                <img src={entry.icon} alt="" className="w-5 h-5 object-contain opacity-70" />
                <span
                  className="font-mono text-[0.68rem] tracking-[0.16em] uppercase transition-colors duration-500"
                  style={{ color: entry.color }}
                >
                  {entry.code}
                </span>
                <span className="text-slate font-mono text-[0.68rem] tracking-[0.12em] uppercase">
                  {tc(entry.metaKey)}
                </span>
                {showStatus && status && (statusKey || status.status_label) && (
                  <span
                    className={`inline-flex items-center font-mono text-[0.68rem] tracking-[0.08em] uppercase px-2 py-0.5 rounded-sm border ${statusClass(status.status_type)}`}
                  >
                    {statusKey ? tc(statusKey) : status.status_label}
                  </span>
                )}
              </div>

              <h2
                className={`font-display text-[clamp(18px,2.2vw,26px)] font-bold leading-snug text-navy transition-transform duration-700 group-hover:translate-x-2 ${isOpen ? 'translate-x-2' : ''}`}
              >
                {tc(entry.titleKey)}
              </h2>
            </div>
          </div>
        </button>

        <AnimatePresence initial={false}>
          {isOpen && (
            <motion.div
              key="content"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
              className="overflow-hidden"
            >
              <div className="pb-8 md:pl-[calc(8.333%+2rem)] md:pr-10">
                <div className="grid gap-6 lg:grid-cols-12 lg:gap-10">
                  <div className="lg:col-span-7">
                    {entry.orgKey && (
                      <p
                        className="font-mono text-xs tracking-[0.1em] uppercase mb-3"
                        style={{ color: entry.color }}
                      >
                        {tc(entry.orgKey)}
                      </p>
                    )}
                    <p className="text-sm text-slate leading-relaxed whitespace-pre-line">
                      {tc(entry.descriptionKey)}
                    </p>
                  </div>

                  <div className="lg:col-span-5">
                    {topics.length > 0 && (
                      <div className="flex flex-wrap gap-2 mb-5">
                        {topics.map((topic) => (
                          <span
                            key={topic}
                            className="text-xs px-3 py-1.5 rounded-full bg-navy/5 text-navy/70"
                          >
                            {topic}
                          </span>
                        ))}
                      </div>
                    )}

                    {(delegates || hasDownloads) && (
                      <div className="flex flex-wrap items-center gap-x-5 gap-y-3 pt-4 border-t border-navy/10">
                        {delegates && (
                          <span className="text-xs text-slate">
                            <strong className="text-navy font-semibold">{delegates}</strong>
                          </span>
                        )}

                        {entry.guide && (
                          <a
                            href={encodeURI(entry.guide)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 text-xs font-medium transition-colors no-underline"
                            style={{ color: entry.color }}
                          >
                            <Download size={13} /> {tc('guide_link')}
                          </a>
                        )}

                        {entry.manual && entry.manual !== entry.guide && (
                          <a
                            href={encodeURI(entry.manual)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 text-xs font-medium text-navy/70 hover:text-navy transition-colors no-underline"
                          >
                            <Download size={13} /> {tc('manual_link')}
                          </a>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

export function ComitesContent() {
  const t = useTranslations('comites');
  const [openId, setOpenId] = useState<string | null>(null);
  const [apiCommittees, setApiCommittees] = useState<CommitteeStatus[]>([]);

  useEffect(() => {
    let cancelled = false;

    async function loadStatus() {
      const data = await api.comites();
      if (!cancelled && data) setApiCommittees(data);
    }

    loadStatus();
    return () => {
      cancelled = true;
    };
  }, []);

  const statusById = useMemo(() => {
    const map = new Map<string, CommitteeStatus | null>();
    for (const entry of committees) {
      map.set(entry.id, matchStatus(entry, apiCommittees));
    }
    return map;
  }, [apiCommittees]);

  const themes = committees.filter((c) => c.section === 'themes');
  const classic = committees.filter((c) => c.section === 'committees');
  const manual = committees.find((c) => c.section === 'manual');

  function toggle(id: string) {
    setOpenId((current) => (current === id ? null : id));
  }

  function renderRow(entry: CommitteeEntry, index: number) {
    return (
      <CommitteeRow
        key={entry.id}
        entry={entry}
        status={statusById.get(entry.id)}
        isOpen={openId === entry.id}
        onToggle={() => toggle(entry.id)}
        delay={index * 0.06}
      />
    );
  }

  return (
    <div className="pt-[68px]">
      <section className="bg-navy py-16 relative overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <span className="font-display text-[120px] md:text-[200px] font-black text-white/[0.03] select-none">
            {t('watermark')}
          </span>
        </div>
        <Container>
          <div className="relative z-10">
            <div className="flex items-center gap-2 text-slate-light text-sm mb-4">
              <Link href="/" className="hover:text-white transition-colors">
                {t('breadcrumb_home')}
              </Link>
              <span>›</span>
              <span className="text-white">{t('breadcrumb_themes')}</span>
            </div>
            <span className="section-label">
              <span className="w-7 h-px bg-gold" />
              {t('hero_label')}
            </span>
            <h1 className="font-display text-[clamp(36px,4vw,56px)] font-bold text-white mb-4">
              {t('hero_title')}
            </h1>
            <p className="text-slate-light text-lg max-w-2xl">{t('hero_sub')}</p>
          </div>
        </Container>
      </section>

      <section className="py-14 bg-surface min-h-[60vh]">
        <Container>
          {manual && (
            <>
              <SectionHeading label={t('section_manual')} />
              <div className="border-t border-navy/10">
                {renderRow(manual, 0)}
              </div>
            </>
          )}

          <SectionHeading label={t('section_themes')} />
          <div className="border-t border-navy/10">
            {themes.map((entry, i) => renderRow(entry, i + (manual ? 1 : 0)))}
          </div>

          <SectionHeading label={t('section_committees')} />
          <div className="border-t border-navy/10">
            {classic.map((entry, i) => renderRow(entry, i + themes.length + (manual ? 1 : 0)))}
          </div>
        </Container>
      </section>
    </div>
  );
}
