'use client';

import { useCallback, useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { AnimatePresence, motion } from 'motion/react';
import { Container } from '@/components/ui/Container';
import Link from 'next/link';
import { X, Quote } from 'lucide-react';

const values = [
  { icon: '/icons/dove.svg', labelKey: 'diplomacia' },
  { icon: '/icons/globe.svg', labelKey: 'diversidade' },
  { icon: '/icons/books.svg', labelKey: 'excelencia' },
  { icon: '/icons/handshake.svg', labelKey: 'cooperacao' },
  { icon: '/icons/leaf.svg', labelKey: 'sustentavel' },
] as const;

const simulationCards = [
  { icon: '/icons/compass.svg', titleKey: 'representacao', descKey: 'representacao_desc' },
  { icon: '/icons/microphone.svg', titleKey: 'debates', descKey: 'debates_desc' },
  { icon: '/icons/handshake.svg', titleKey: 'negociacao', descKey: 'negociacao_desc' },
  { icon: '/icons/scroll.svg', titleKey: 'resolucoes', descKey: 'resolucoes_desc' },
];

const ANGELA = {
  name: 'Angela Jasper',
  roleKey: 'role_professora',
  quoteKey: 'angela_quote',
};

const currentTeam = [
  { name: 'Guilherme Santiago', roleKey: 'role_secretario', photo: '/img/equipe/santiago.jpg', quoteKey: 'team_current.0.quote' },
  { name: 'Eloisa Monteiro', roleKey: 'role_diretora_eventos', photo: '/img/equipe/Eloisa.jpg', quoteKey: 'team_current.1.quote' },
  { name: 'Giovana Rodrigues', roleKey: 'role_diretora_rp', photo: '/img/equipe/Gi.jpg', quoteKey: 'team_current.2.quote' },
  { name: 'Talita Marcelino', roleKey: 'role_hr', photo: '/img/equipe/Talita.jpg', quoteKey: 'team_current.3.quote' },
  { name: 'Julia Marson', roleKey: 'role_admin', photo: '/img/equipe/Julia_3.png', quoteKey: 'team_current.4.quote' },
  { name: 'Pedro Bonazzi', roleKey: 'role_staff_web', quoteKey: 'team_current.5.quote' },
  { name: 'Mariana Cerqueira', roleKey: 'role_membro', quoteKey: 'team_current.6.quote' },
  { name: 'Kauã Santos', roleKey: 'role_membro', quoteKey: 'team_current.7.quote' },
  { name: 'Maria Macaúba', roleKey: 'role_membro', quoteKey: 'team_current.8.quote' },
  { name: 'Aline Cristina', roleKey: 'role_membro', quoteKey: 'team_current.9.quote' },
  { name: 'Júlia Morales', roleKey: 'role_membro', quoteKey: 'team_current.10.quote' },
  { name: 'Luccas Montezini', roleKey: 'role_membro', quoteKey: 'team_current.11.quote' },
  { name: 'Laura Valk', roleKey: 'role_membro', quoteKey: 'team_current.12.quote' },
  { name: 'Gabrielly Viana', roleKey: 'role_membro', quoteKey: 'team_current.13.quote' },
  { name: 'Maria Eduarda Cirico', roleKey: 'role_membro', quoteKey: 'team_current.14.quote' },
  { name: 'Maria Gabi', roleKey: 'role_membro', quoteKey: 'team_current.15.quote' },
  { name: 'Rafael Fernando', roleKey: 'role_membro', quoteKey: 'team_current.16.quote' },
  { name: 'Bianca Mafra', roleKey: 'role_membro', photo: '/img/equipe/MAFRA.png', quoteKey: 'team_current.17.quote' },
];

const team2025 = [
  { name: 'Guilherme Santiago', roleKey: 'role_secretario', photo: '/img/equipe/santiago.jpg', quoteKey: 'team_2025.0.quote' },
  { name: 'Emilly', roleKey: 'role_diretora_academica', quoteKey: 'team_2025.1.quote' },
  { name: 'Eloisa Monteiro', roleKey: 'role_diretora_eventos', photo: '/img/equipe/Eloisa.jpg', quoteKey: 'team_2025.2.quote' },
  { name: 'Manuella Barros', roleKey: 'role_comm', quoteKey: 'team_2025.3.quote' },
  { name: 'Giovana Rodrigues', roleKey: 'role_diretora_rp', photo: '/img/equipe/Gi.jpg', quoteKey: 'team_2025.4.quote' },
  { name: 'Talita Marcelino', roleKey: 'role_hr', photo: '/img/equipe/Talita.jpg', quoteKey: 'team_2025.5.quote' },
  { name: 'Julia Marson', roleKey: 'role_admin', photo: '/img/equipe/Julia_3.png', quoteKey: 'team_2025.6.quote' },
  { name: 'Emanuelle', roleKey: 'role_staff_coord', quoteKey: 'team_2025.7.quote' },
  { name: 'Pedro Bonazzi', roleKey: 'role_staff_web', quoteKey: 'team_2025.8.quote' },
];

const LEADERSHIP_ROLE_KEYS = [
  'role_secretario',
  'role_diretora_academica',
  'role_diretora_eventos',
  'role_comm',
  'role_diretora_rp',
  'role_hr',
  'role_admin',
  'role_staff_coord',
  'role_staff_web',
];

function isLeadership(roleKey: string) {
  return LEADERSHIP_ROLE_KEYS.includes(roleKey);
}

function getInitials(name: string) {
  return name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase();
}

interface TestimonialMember {
  name: string;
  roleKey: string;
  photo?: string;
  quoteKey?: string;
}

export function SobreContent() {
  const t = useTranslations('sobre');
  const tc = useTranslations('common');
  const tv = useTranslations('sobre_values');
  const [activeTab, setActiveTab] = useState<'current' | '2025'>('current');
  const [selected, setSelected] = useState<TestimonialMember | null>(null);
  const team = activeTab === 'current' ? currentTeam : team2025;

  const closeSelected = useCallback(() => setSelected(null), []);

  useEffect(() => {
    if (!selected) return;

    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') closeSelected();
    }

    document.addEventListener('keydown', onKey);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', onKey);
      document.body.style.overflow = '';
    };
  }, [selected, closeSelected]);

  return (
    <div className="pt-[68px]">
      {/* Hero */}
      <section className="bg-navy py-16 relative overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <span className="font-display text-[120px] md:text-[200px] font-black text-white/[0.03] select-none">
            {t('watermark')}
          </span>
        </div>
        <Container>
          <div className="relative z-10">
            <div className="flex items-center gap-2 text-slate-light text-sm mb-4">
              <Link href="/" className="hover:text-white transition-colors">{tc('home')}</Link>
              <span>›</span>
              <span className="text-white">{t('breadcrumb_about')}</span>
            </div>
            <span className="section-label">
              <span className="w-7 h-px bg-gold" />
              {t('hero_label')}
            </span>
            <h1 className="font-display text-[clamp(36px,4vw,56px)] font-bold text-white mb-4">
              {t('hero_title')}
            </h1>
            <p className="text-slate-light text-lg">{t('hero_sub')}</p>
          </div>
        </Container>
      </section>

      {/* Mission & Vision */}
      <section className="py-16 bg-white">
        <Container>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5 }}
              className="p-8 rounded-xl border-t-4 border-navy bg-surface"
            >
              <div className="w-14 h-14 rounded-full bg-navy/10 flex items-center justify-center mb-5">
                <img src="/icons/target.svg" alt="" className="w-7 h-7" />
              </div>
              <h2 className="font-display text-xl font-bold text-navy mb-3">{t('mission')}</h2>
              <p className="text-slate leading-relaxed">{t('mission_desc')}</p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="p-8 rounded-xl border-t-4 border-gold bg-surface"
            >
              <div className="w-14 h-14 rounded-full bg-gold/10 flex items-center justify-center mb-5">
                <img src="/icons/telescope.svg" alt="" className="w-7 h-7" />
              </div>
              <h2 className="font-display text-xl font-bold text-navy mb-3">{t('vision')}</h2>
              <p className="text-slate leading-relaxed">{t('vision_desc')}</p>
            </motion.div>
          </div>
        </Container>
      </section>

      {/* Values */}
      <section className="py-16 bg-navy">
        <Container>
          <div className="text-center mb-12">
            <span className="section-label justify-center">
              <span className="w-7 h-px bg-gold" />
              {t('values')}
            </span>
            <h2 className="section-title text-white">{t('values_title')}</h2>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {values.map((value, i) => {
              const label = tv(value.labelKey);
              return (
                <motion.div
                  key={value.labelKey}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: i * 0.08 }}
                  className="bg-navy-mid/50 border border-white/10 rounded-lg p-5 text-center hover:bg-navy-mid transition-all"
                >
                  <img src={value.icon} alt={label} className="w-8 h-8 mx-auto mb-3 opacity-80" />
                  <span className="text-sm text-white font-medium">{label}</span>
                </motion.div>
              );
            })}
          </div>
        </Container>
      </section>

      {/* History */}
      <section className="py-16 bg-white">
        <Container>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6 }}
              className="bg-surface rounded-xl p-8 border border-navy/5"
            >
              <div className="flex items-center gap-3 mb-6">
                <span className="bg-navy text-white text-sm font-bold px-4 py-1.5 rounded">
                  {t('founding_badge')}
                </span>
                <span className="text-sm text-slate">SESI CE-437</span>
              </div>
              <div className="space-y-4 text-slate leading-relaxed">
                <p>{t('history_p1')}</p>
                <p>{t('history_p2')}</p>
                <p>{t('history_p3')}</p>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-8 pt-6 border-t border-navy/10">
                <div className="text-center">
                  <span className="block text-2xl font-display font-bold text-navy">2024</span>
                  <span className="text-xs text-slate">{t('fundacao_ano')}</span>
                </div>
                <div className="text-center">
                  <span className="block text-2xl font-display font-bold text-navy">CE-437</span>
                  <span className="text-xs text-slate">{t('unidade')}</span>
                </div>
                <div className="text-center">
                  <span className="block text-2xl font-display font-bold text-navy">6º+</span>
                  <span className="text-xs text-slate">{t('edicoes_realizadas')}</span>
                </div>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              <span className="section-label">
                <span className="w-7 h-px bg-gold" />
                {t('history')}
              </span>
              <h2 className="section-title">{t('history_desc')}</h2>
              <p className="section-body mb-6">{t('history_body')}</p>
              <Link
                href="/faca-parte"
                className="inline-flex items-center gap-2 text-[#7a5f1f] font-medium hover:text-[#4a380c] transition-colors no-underline"
              >
                {t('join_cta')}
              </Link>
            </motion.div>
          </div>
        </Container>
      </section>

      {/* What is a UN Simulation */}
      <section className="py-16 bg-surface">
        <Container>
          <div className="text-center mb-12">
            <span className="section-label justify-center">
              <span className="w-7 h-px bg-gold" />
              {t('simulacao')}
            </span>
            <h2 className="section-title">{t('how_it_works')}</h2>
            <p className="section-body mx-auto">{t('simulacao_desc')}</p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {simulationCards.map((card, i) => (
              <motion.div
                key={card.titleKey}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="bg-white rounded-xl p-6 border border-navy/5 text-center hover:shadow-elevated transition-all duration-300"
              >
                <div className="w-14 h-14 rounded-full bg-gold/10 flex items-center justify-center mx-auto mb-4">
                  <img src={card.icon} alt="" className="w-7 h-7" />
                </div>
                <h3 className="font-display text-lg font-bold text-navy mb-2">{t(card.titleKey)}</h3>
                <p className="text-sm text-slate leading-relaxed">{t(card.descKey)}</p>
              </motion.div>
            ))}
          </div>
        </Container>
      </section>

      {/* Team */}
      <section className="py-16 bg-white">
        <Container>
          <div className="text-center mb-8">
            <span className="section-label justify-center">
              <span className="w-7 h-px bg-gold" />
              {t('team')}
            </span>
            <h2 className="section-title">{t('team_who')}</h2>
          </div>

          {/* Tabs */}
          <div className="flex justify-center gap-4 mb-10">
            <button
              onClick={() => setActiveTab('current')}
              className={`px-6 py-2.5 rounded-full text-sm font-medium transition-all ${
                activeTab === 'current' ? 'bg-navy text-white' : 'bg-surface text-navy hover:bg-surface-alt'
              }`}
            >
              {t('tab_current')}
            </button>
            <button
              onClick={() => setActiveTab('2025')}
              className={`px-6 py-2.5 rounded-full text-sm font-medium transition-all ${
                activeTab === '2025' ? 'bg-navy text-white' : 'bg-surface text-navy hover:bg-surface-alt'
              }`}
            >
              {t('tab_2025')}
            </button>
          </div>

          {/* Featured teacher — responsável pela equipe no ano ativo */}
          <motion.button
            type="button"
            key={`featured-${activeTab}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            onClick={() => setSelected(ANGELA)}
            className="group relative block w-full max-w-3xl mx-auto mb-10 text-left overflow-hidden bg-gradient-to-br from-navy to-navy-mid rounded-2xl p-8 md:p-10 border border-gold/20 shadow-elevated transition-all duration-300 hover:border-gold/50 hover:shadow-glow focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gold/60"
          >
            <span
              aria-hidden="true"
              className="absolute top-0 left-0 h-full w-1.5 bg-gold"
            />
            <div className="absolute inset-0 pointer-events-none opacity-[0.06]">
              <span className="absolute -right-6 -top-6 font-display text-[140px] font-black text-white select-none">
                AJ
              </span>
            </div>

            <div className="relative flex flex-col sm:flex-row items-start gap-6">
              <div className="w-24 h-24 rounded-full bg-gold/15 border-2 border-gold/40 flex items-center justify-center shrink-0">
                <span className="text-3xl font-display font-bold text-gold">AJ</span>
              </div>
              <div className="min-w-0 flex-1">
                <span className="inline-flex items-center gap-1.5 font-mono text-[0.72rem] tracking-[0.16em] uppercase text-gold/90 bg-gold/10 border border-gold/25 px-2.5 py-1 rounded-sm mb-3">
                  {t('role_professora')}
                </span>
                <h3 className="font-display text-2xl md:text-3xl font-bold text-white mb-3">
                  Angela Jasper
                </h3>
                <p className="text-sm md:text-base text-slate-light leading-relaxed max-w-xl mb-4">
                  {t('angela_bio')}
                </p>
                <span className="inline-flex items-center gap-1.5 font-mono text-[0.72rem] tracking-[0.14em] uppercase text-gold/80 group-hover:text-gold transition-colors">
                   <Quote size={12} /> {tc('read_testimonial')}
                </span>
              </div>
            </div>
          </motion.button>

          {/* Team grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {team.map((member, i) => {
              const leadership = isLeadership(member.roleKey);

              return (
                <motion.button
                  type="button"
                  key={member.name}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.3, delay: i * 0.03 }}
                  onClick={() => setSelected(member)}
                  aria-label={t('read_testimonial', { name: member.name })}
                  className={`group relative flex flex-col items-center text-center rounded-xl border p-5 transition-all duration-300 hover:-translate-y-1 hover:shadow-elevated focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gold/50 cursor-pointer ${
                    leadership
                      ? 'bg-surface border-navy/10 hover:border-gold/40'
                      : 'bg-white border-navy/5 hover:border-navy/15'
                  }`}
                >
                  {leadership && (
                    <span
                      aria-hidden="true"
                      className="absolute top-0 left-1/2 -translate-x-1/2 h-0.5 w-10 rounded-b bg-gold opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    />
                  )}

                  <div
                    className={`relative rounded-full overflow-hidden mb-4 flex items-center justify-center shrink-0 ${
                      leadership
                        ? 'bg-gradient-to-br from-navy/15 to-gold/20 ring-2 ring-gold/30'
                        : 'bg-gradient-to-br from-navy/10 to-navy/5 ring-1 ring-navy/10'
                    }`}
                    style={{ width: 72, height: 72 }}
                  >
                    <span
                      className={`absolute inset-0 flex items-center justify-center font-display font-bold ${
                        leadership ? 'text-navy/70 text-lg' : 'text-navy/50 text-base'
                      }`}
                    >
                      {getInitials(member.name)}
                    </span>
                    {member.photo && (
                      <img
                        src={member.photo}
                        alt={member.name}
                        loading="lazy"
                        className="relative w-full h-full object-cover"
                        onError={(e) => {
                          (e.currentTarget as HTMLImageElement).style.display = 'none';
                        }}
                      />
                    )}
                  </div>

                  <h3 className="font-medium text-navy text-sm leading-snug mb-2 px-1">
                    {member.name}
                  </h3>

                  <span
                    className={`mt-auto inline-block font-mono text-[0.68rem] tracking-[0.1em] uppercase px-2 py-1 rounded-sm leading-tight ${
                      leadership
                        ? 'bg-navy/8 text-navy/80 border border-navy/10'
                        : 'bg-slate/10 text-slate'
                    }`}
                  >
                    {t(member.roleKey)}
                  </span>

                  <span className="mt-2 font-mono text-[0.68rem] tracking-[0.12em] uppercase text-gold/0 group-hover:text-gold-dark/90 transition-colors">
                    {tc('read_testimonial')}
                  </span>
                </motion.button>
              );
            })}
          </div>
        </Container>
      </section>

      {/* Testimonial modal */}
      <AnimatePresence>
        {selected && (
          <motion.div
            className="fixed inset-0 z-[200] flex items-center justify-center p-4 sm:p-6"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            <button
              type="button"
              aria-label={tc('close')}
              onClick={closeSelected}
              className="absolute inset-0 bg-navy-dark/70 backdrop-blur-sm cursor-default"
            />

            <motion.div
              role="dialog"
              aria-modal="true"
              aria-label={t('testimonial_of', { name: selected.name })}
              initial={{ opacity: 0, y: 24, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 16, scale: 0.98 }}
              transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
              className="relative w-full max-w-lg bg-white rounded-2xl border border-navy/10 shadow-elevated overflow-hidden"
            >
              <span
                aria-hidden="true"
                className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-gold via-gold-light to-gold"
              />

              <button
                type="button"
                onClick={closeSelected}
                aria-label={tc('close')}
                className="absolute top-4 right-4 z-10 w-9 h-9 rounded-full bg-surface border border-navy/10 flex items-center justify-center text-navy/60 hover:text-navy hover:bg-navy/5 transition-colors"
              >
                <X size={16} />
              </button>

              <div className="p-7 sm:p-9">
                <div className="flex items-start gap-4 mb-6 pr-10">
                  <div
                    className={`relative rounded-full overflow-hidden flex items-center justify-center shrink-0 ${
                      isLeadership(selected.roleKey) || selected.name === ANGELA.name
                        ? 'bg-gradient-to-br from-navy/15 to-gold/20 ring-2 ring-gold/30'
                        : 'bg-gradient-to-br from-navy/10 to-navy/5 ring-1 ring-navy/10'
                    }`}
                    style={{ width: 64, height: 64 }}
                  >
                    <span className="absolute inset-0 flex items-center justify-center font-display font-bold text-navy/60">
                      {getInitials(selected.name)}
                    </span>
                    {selected.photo && (
                      <img
                        src={selected.photo}
                        alt={selected.name}
                        className="relative w-full h-full object-cover"
                        onError={(e) => {
                          (e.currentTarget as HTMLImageElement).style.display = 'none';
                        }}
                      />
                    )}
                  </div>
                  <div className="min-w-0">
                    <span
                      className={`inline-block font-mono text-[0.72rem] tracking-[0.12em] uppercase px-2 py-1 rounded-sm mb-2 ${
                        isLeadership(selected.roleKey) || selected.name === ANGELA.name
                          ? 'bg-navy/8 text-navy/80 border border-navy/10'
                          : 'bg-slate/10 text-slate'
                      }`}
                    >
                      {t(selected.roleKey)}
                    </span>
                    <h3 className="font-display text-xl font-bold text-navy leading-snug">
                      {selected.name}
                    </h3>
                  </div>
                </div>

                <div className="relative">
                  <Quote
                    size={36}
                    className="absolute -top-1 -left-1 text-gold/25"
                    aria-hidden="true"
                  />
                  <p className="relative pl-8 text-[15px] sm:text-base text-navy/80 leading-relaxed italic">
                    {selected.quoteKey ? t(selected.quoteKey) : ''}
                  </p>
                </div>

                <div className="mt-7 pt-5 border-t border-navy/10 flex justify-end">
                  <button
                    type="button"
                    onClick={closeSelected}
                    className="btn btn-navy text-xs"
                  >
                    {tc('close')}
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
