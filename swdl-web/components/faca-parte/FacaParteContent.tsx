'use client';

import { useState, useEffect, useMemo } from 'react';
import { useTranslations } from 'next-intl';
import { motion } from 'motion/react';
import { api, EventConfig } from '@/lib/api';
import { Container } from '@/components/ui/Container';
import { LinkButton } from '@/components/ui/Button';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Check, ArrowRight } from 'lucide-react';
import Link from 'next/link';

type DelegateFormData = z.infer<ReturnType<typeof makeDelegateSchema>>;

const emptyMember = {
  name: '',
  email: '',
  phone: '',
  instagram: '',
  grade: '',
  motivation: '',
};

function makeDelegateSchema(t: (k: string) => string) {
  const memberSchema = z.object({
    name: z.string().min(3, t('zod_name')),
    email: z.string().email(t('zod_email')),
    phone: z.string().min(10, t('zod_phone')),
    instagram: z.string().min(1, t('zod_instagram')),
    grade: z.string().optional(),
    motivation: z.string().optional(),
  });

  return z
    .object({
      name: z.string().min(3, t('zod_name')),
      email: z.string().email(t('zod_email')),
      phone: z.string().min(10, t('zod_phone')),
      instagram: z.string().min(1, t('zod_instagram')),
      school: z.string().optional(),
      grade: z.string().optional(),
      experience: z.string().optional(),
      interests: z.string().optional(),
      motivation: z.string().optional(),
      formato: z.enum(['individual', 'dupla', 'trio']),
      members: z.array(memberSchema).default([]),
      accept_terms: z.boolean().refine((val) => val === true, t('zod_terms')),
    })
    .superRefine((val, ctx) => {
      const expected =
        val.formato === 'dupla' ? 1 : val.formato === 'trio' ? 2 : 0;
      if (val.members.length !== expected) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ['members'],
          message: t('zod_members_count'),
        });
      }
    });
}

const formats = [
  { id: 'individual', icon: '/icons/individual.svg', label: 'format_individual' },
  { id: 'dupla', icon: '/icons/dupla.svg', label: 'format_dupla' },
  { id: 'trio', icon: '/icons/trio.svg', label: 'format_trio' },
];

const requirementsKeys = [
  { icon: '/icons/school.svg', title: 'req_school', desc: 'req_school_desc' },
  { icon: '/icons/calendar.svg', title: 'req_disponibilidade', desc: 'req_disponibilidade_desc' },
  { icon: '/icons/books.svg', title: 'req_comprometimento', desc: 'req_comprometimento_desc' },
  { icon: '/icons/handshake.svg', title: 'req_equipe', desc: 'req_equipe_desc' },
] as const;

const volunteerRoleKeys = [
  { icon: '/icons/microphone.svg', title: 'role_moderador', desc: 'role_moderador_desc' },
  { icon: '/icons/camera.svg', title: 'role_midia', desc: 'role_midia_desc' },
  { icon: '/icons/clipboard.svg', title: 'role_organizacao', desc: 'role_organizacao_desc' },
  { icon: '/icons/star.svg', title: 'role_mentor', desc: 'role_mentor_desc' },
] as const;

const stepKeys = [
  { num: 1, title: 'step_1', desc: 'step_1_desc' },
  { num: 2, title: 'step_2', desc: 'step_2_desc' },
  { num: 3, title: 'step_3', desc: 'step_3_desc' },
  { num: 4, title: 'step_4', desc: 'step_4_desc' },
] as const;

const gradeLabels = [
  '6º Ano', '7º Ano', '8º Ano', '9º Ano',
  '1º Ano EM', '2º Ano EM', '3º Ano EM',
] as const;

const INSCRICOES_FECHADAS = false; // toggle temporário: true mostra “Inscrições Fechadas”

export function FacaParteContent() {
  const t = useTranslations('faca_parte');
  const tc = useTranslations('common');
  const [config, setConfig] = useState<EventConfig | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [sending, setSending] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'delegado' | 'voluntario'>('delegado');

  const delegateSchema = useMemo(() => makeDelegateSchema(t), [t]);
  const gradeOptions = useMemo(
    () => gradeLabels.map((_, i) => t(`grades.${i}`)),
    [t]
  );

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    getValues,
    control,
    formState: { errors },
  } = useForm<DelegateFormData>({
    resolver: zodResolver(delegateSchema),
    defaultValues: { formato: 'individual', members: [] },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'members',
  });

  const selectedFormat = watch('formato');
  const memberCount =
    selectedFormat === 'dupla' ? 1 : selectedFormat === 'trio' ? 2 : 0;

  useEffect(() => {
    const current = getValues('members') || [];
    if (current.length > memberCount) {
      for (let i = current.length - 1; i >= memberCount; i--) remove(i);
    } else if (current.length < memberCount) {
      for (let i = current.length; i < memberCount; i++) append({ ...emptyMember });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [memberCount]);

  useEffect(() => {
    async function loadConfig() {
      const data = await api.config();
      if (data) setConfig(data);
    }
    loadConfig();
  }, []);

  const onSubmit = async (data: DelegateFormData) => {
    setSending(true);
    setServerError(null);
    const payload = {
      ...data,
      type: activeTab === 'voluntario' ? 'volunteer' : 'delegate',
      accept_terms: true,
      members:
        activeTab === 'voluntario' || data.formato === 'individual'
          ? []
          : data.members,
      formato: activeTab === 'voluntario' ? 'individual' : data.formato,
    };
    const result = await api.inscrever(payload);
    setSending(false);
    if (result?.ok) {
      setSubmitted(true);
    } else {
      setServerError(result?.error || t('form_error'));
    }
  };

  if (INSCRICOES_FECHADAS) {
    return (
      <div className="pt-[68px] min-h-screen flex items-center justify-center bg-surface">
        <Container>
          <div className="text-center py-16">
            <h1 className="font-display text-3xl font-bold text-navy mb-4">{t('closed_title')}</h1>
            <p className="text-slate mb-8">{t('closed_desc')}</p>
            <LinkButton href="/" variant="primary">{tc('back_home')}</LinkButton>
          </div>
        </Container>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="pt-[68px] min-h-screen flex items-center justify-center bg-surface">
        <Container>
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="text-center py-16">
            <div className="w-20 h-20 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-6">
              <Check className="w-10 h-10 text-green-700" />
            </div>
            <h1 className="font-display text-3xl font-bold text-navy mb-4">{t('form_success')}</h1>
            <p className="text-slate mb-8 max-w-md mx-auto">{t('form_success_msg')}</p>
            <LinkButton href="/" variant="primary">{tc('back_home')}</LinkButton>
          </motion.div>
        </Container>
      </div>
    );
  }

  return (
    <div className="pt-[68px]">
      {/* Hero */}
      <section className="bg-navy py-16 relative overflow-hidden">
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <span className="font-display text-[80px] md:text-[140px] font-black text-white/[0.03] select-none">
            FAÇA PARTE
          </span>
        </div>
        <Container>
          <div className="relative z-10">
            <div className="flex items-center gap-2 text-slate-light text-sm mb-4">
              <Link href="/" className="hover:text-white transition-colors">{tc('home')}</Link>
              <span>›</span>
              <span className="text-white">{t('hero_title')}</span>
            </div>
            <span className="section-label">
              <span className="w-7 h-px bg-gold" />
              {t('hero_label')}
            </span>
            <h1 className="font-display text-[clamp(36px,4vw,56px)] font-bold text-white mb-4">{t('hero_title')}</h1>
            <p className="text-slate-light text-lg">{t('hero_sub')}</p>
          </div>
        </Container>
      </section>

      {/* Tabs */}
      <section className="bg-white border-b border-navy/5 sticky top-[68px] z-30">
        <Container>
          <div className="flex gap-0">
            <button
              onClick={() => {
                setActiveTab('delegado');
                setServerError(null);
              }}
              className={`flex-1 py-4 text-sm font-medium transition-all border-b-2 ${
                activeTab === 'delegado' ? 'border-gold text-navy' : 'border-transparent text-slate hover:text-navy'
              }`}
            >
              {t('tab_delegado')}
            </button>
            <button
              onClick={() => {
                setActiveTab('voluntario');
                setValue('formato', 'individual');
                setServerError(null);
              }}
              className={`flex-1 py-4 text-sm font-medium transition-all border-b-2 ${
                activeTab === 'voluntario' ? 'border-gold text-navy' : 'border-transparent text-slate hover:text-navy'
              }`}
            >
              {t('tab_voluntario')}
            </button>
          </div>
        </Container>
      </section>

      {/* Why Delegate */}
      {activeTab === 'delegado' && (
        <section className="py-12 bg-surface">
          <Container>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
              <div>
                <h2 className="font-display text-2xl font-bold text-navy mb-6">{t('why_delegate')}</h2>
                <div className="space-y-3 mb-10">
                  {(t.raw('why_reasons') as string[]).map((reason, i) => (
                    <motion.div key={i} initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.3, delay: i * 0.05 }} className="flex items-start gap-3">
                      <Check className="w-5 h-5 text-green-700 shrink-0 mt-0.5" />
                      <span className="text-slate text-sm">{reason}</span>
                    </motion.div>
                  ))}
                </div>

                <h3 className="font-display text-xl font-bold text-navy mb-4">{t('requirements')}</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {requirementsKeys.map((req, i) => (
                    <motion.div key={req.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.4, delay: i * 0.1 }} className="bg-white rounded-lg p-4 border border-navy/5">
                      <img src={req.icon} alt="" className="w-6 h-6 mb-2" />
                      <h4 className="font-medium text-navy text-sm mb-1">{t(req.title)}</h4>
                      <p className="text-xs text-slate">{t(req.desc)}</p>
                    </motion.div>
                  ))}
                </div>
              </div>

              <div>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-navy mb-3">{t('format_selector')}</label>
                    <div className="grid grid-cols-3 gap-3">
                      {formats.map((format) => (
                        <button key={format.id} type="button" onClick={() => setValue('formato', format.id as any)} className={`p-4 rounded-lg border-2 transition-all text-center ${selectedFormat === format.id ? 'border-gold bg-gold/5' : 'border-navy/10 hover:border-navy/20'}`}>
                          <img src={format.icon} alt="" className={`w-6 h-6 mx-auto mb-2 ${selectedFormat === format.id ? '' : 'opacity-50'}`} />
                          <span className="text-xs font-medium text-navy">{t(format.label)}</span>
                        </button>
                      ))}
                    </div>
                  </div>

                  {memberCount > 0 && (
                    <div>
                      <label className="block text-sm font-medium text-navy mb-3">{t('members_title')}</label>
                      <div className="space-y-4">
                        {fields.map((field, i) => (
                          <div key={field.id} className="rounded-xl border border-navy/10 bg-surface p-5 sm:p-6 shadow-card">
                            <p className="inline-flex items-center gap-2 text-[11px] font-mono font-bold tracking-[0.12em] uppercase text-gold-dark bg-gold/10 border border-gold/30 rounded-sm px-2.5 py-1 mb-4">
                              {t('member_card_label', { index: i + 1 })}
                            </p>
                            <div className="space-y-3">
                              <div>
                                <label className="block text-xs font-medium text-navy mb-1">{t('form_name')} *</label>
                                <input {...register(`members.${i}.name` as const)} className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all" placeholder={t('form_name')} />
                                {errors.members?.[i]?.name && <p className="text-red-700 text-xs mt-1">{errors.members[i]?.name?.message}</p>}
                              </div>
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                  <label className="block text-xs font-medium text-navy mb-1">{t('form_email')} *</label>
                                  <input {...register(`members.${i}.email` as const)} type="email" className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all" placeholder="seu@email.com" />
                                  {errors.members?.[i]?.email && <p className="text-red-700 text-xs mt-1">{errors.members[i]?.email?.message}</p>}
                                </div>
                                <div>
                                  <label className="block text-xs font-medium text-navy mb-1">{t('form_phone')} *</label>
                                  <input {...register(`members.${i}.phone` as const)} type="tel" className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all" placeholder="(85) 99999-9999" />
                                  {errors.members?.[i]?.phone && <p className="text-red-700 text-xs mt-1">{errors.members[i]?.phone?.message}</p>}
                                </div>
                              </div>
                              <div>
                                <label className="block text-xs font-medium text-navy mb-1">{t('form_instagram')} *</label>
                                <input {...register(`members.${i}.instagram` as const)} className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all" placeholder="@seuinstagram" />
                                {errors.members?.[i]?.instagram && <p className="text-red-700 text-xs mt-1">{errors.members[i]?.instagram?.message}</p>}
                              </div>
                              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div>
                                  <label className="block text-xs font-medium text-navy mb-1">{t('form_grade')}</label>
                                  <select {...register(`members.${i}.grade` as const)} className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all bg-white">
                                    <option value="">{t('form_grade_select')}</option>
                                    {gradeOptions.map(g => <option key={g} value={g}>{g}</option>)}
                                  </select>
                                </div>
                                <div>
                                  <label className="block text-xs font-medium text-navy mb-1">{t('form_motivation')}</label>
                                  <input {...register(`members.${i}.motivation` as const)} className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all" placeholder={t('form_motivation')} />
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                      {errors.members && !Array.isArray(errors.members) && typeof errors.members.message === 'string' && (
                        <p className="text-red-700 text-xs mt-2">{errors.members.message}</p>
                      )}
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-medium text-navy mb-1.5">{t('form_name')} *</label>
                    <input {...register('name')} className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all" placeholder={t('form_name')} />
                    {errors.name && <p className="text-red-700 text-xs mt-1">{errors.name.message}</p>}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-navy mb-1.5">{t('form_email')} *</label>
                      <input {...register('email')} type="email" className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all" placeholder="seu@email.com" />
                      {errors.email && <p className="text-red-700 text-xs mt-1">{errors.email.message}</p>}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-navy mb-1.5">{t('form_phone')} *</label>
                      <input {...register('phone')} type="tel" className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all" placeholder="(85) 99999-9999" />
                      {errors.phone && <p className="text-red-700 text-xs mt-1">{errors.phone.message}</p>}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-navy mb-1.5">{t('form_instagram')}</label>
                    <input {...register('instagram')} className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all" placeholder="@seuinstagram" />
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-navy mb-1.5">{t('form_school')}</label>
                      <input {...register('school')} className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all" placeholder={t('form_school')} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-navy mb-1.5">{t('form_grade')}</label>
                      <select {...register('grade')} className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all bg-white">
                        <option value="">{t('form_grade_select')}</option>
                        {gradeOptions.map(g => <option key={g} value={g}>{g}</option>)}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-navy mb-1.5">{t('form_experience')}</label>
                    <textarea {...register('experience')} rows={3} className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all resize-none" placeholder={t('form_experience_placeholder')} />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-navy mb-1.5">{t('form_interests')}</label>
                    <textarea {...register('interests')} rows={2} className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all resize-none" placeholder={t('form_interests_placeholder')} />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-navy mb-1.5">{t('form_motivation')}</label>
                    <textarea {...register('motivation')} rows={3} className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all resize-none" placeholder={t('form_motivation')} />
                  </div>

                  <div className="flex items-start gap-3">
                    <input type="checkbox" {...register('accept_terms')} className="mt-1 w-4 h-4 text-gold-dark border-navy/30 rounded focus:ring-gold-dark" />
                    <label className="text-sm text-slate">{t('form_terms')}</label>
                  </div>
                  {errors.accept_terms && <p className="text-red-700 text-xs">{errors.accept_terms.message}</p>}

                  {serverError && (
                    <p className="text-red-700 text-sm bg-red-50 border border-red-200 rounded-lg px-4 py-3">{serverError}</p>
                  )}

                  <button type="submit" disabled={sending} className="w-full btn-primary justify-center py-4 text-base disabled:opacity-50 disabled:cursor-not-allowed">
                    {sending ? t('form_sending') : t('form_submit')}
                  </button>
                </form>
              </div>
            </div>
          </Container>
        </section>
      )}

      {/* Volunteer */}
      {activeTab === 'voluntario' && (
        <section className="py-12 bg-surface">
          <Container>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
              <div>
                <h2 className="font-display text-2xl font-bold text-navy mb-6">{t('volunteer_roles')}</h2>
                <div className="space-y-4 mb-10">
                  {volunteerRoleKeys.map((role, i) => (
                    <motion.div key={role.title} initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ duration: 0.4, delay: i * 0.1 }} className="bg-white rounded-lg p-5 border border-navy/5 flex items-start gap-4">
                      <div className="w-12 h-12 rounded-full bg-gold/10 flex items-center justify-center shrink-0">
                        <img src={role.icon} alt="" className="w-6 h-6" />
                      </div>
                      <div>
                        <h3 className="font-medium text-navy mb-1">{t(role.title)}</h3>
                        <p className="text-sm text-slate">{t(role.desc)}</p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>

              <div>
                <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
                  <div>
                    <label className="block text-sm font-medium text-navy mb-1.5">{t('form_name')} *</label>
                    <input {...register('name')} className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all" placeholder={t('form_name')} />
                    {errors.name && <p className="text-red-700 text-xs mt-1">{errors.name.message}</p>}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-navy mb-1.5">{t('form_email')} *</label>
                      <input {...register('email')} type="email" className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all" placeholder="seu@email.com" />
                      {errors.email && <p className="text-red-700 text-xs mt-1">{errors.email.message}</p>}
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-navy mb-1.5">{t('form_phone')} *</label>
                      <input {...register('phone')} type="tel" className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all" placeholder="(85) 99999-9999" />
                      {errors.phone && <p className="text-red-700 text-xs mt-1">{errors.phone.message}</p>}
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-navy mb-1.5">{t('form_instagram')}</label>
                    <input {...register('instagram')} className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all" placeholder="@seuinstagram" />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-navy mb-1.5">{t('form_grade')}</label>
                    <select {...register('grade')} className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all bg-white">
                      <option value="">{t('form_grade_select')}</option>
                      {gradeOptions.map(g => <option key={g} value={g}>{g}</option>)}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-navy mb-1.5">{t('form_motivation')}</label>
                    <textarea {...register('motivation')} rows={4} className="w-full px-4 py-3 rounded-lg border border-navy/10 focus:border-gold focus:ring-2 focus:ring-gold/20 outline-none transition-all resize-none" placeholder={t('form_motivation_volunteer')} />
                  </div>

                  <div className="flex items-start gap-3">
                    <input type="checkbox" {...register('accept_terms')} className="mt-1 w-4 h-4 text-gold-dark border-navy/30 rounded focus:ring-gold-dark" />
                    <label className="text-sm text-slate">{t('form_terms')}</label>
                  </div>
                  {errors.accept_terms && <p className="text-red-700 text-xs">{errors.accept_terms.message}</p>}

                  {serverError && (
                    <p className="text-red-700 text-sm bg-red-50 border border-red-200 rounded-lg px-4 py-3">{serverError}</p>
                  )}

                  <button type="submit" disabled={sending} className="w-full btn-primary justify-center py-4 text-base disabled:opacity-50 disabled:cursor-not-allowed">
                    {sending ? t('form_sending') : t('form_submit_volunteer')}
                  </button>
                </form>
              </div>
            </div>
          </Container>
        </section>
      )}

      {/* Steps */}
      <section className="py-16 bg-white">
        <Container>
          <div className="text-center mb-10">
            <h2 className="section-title">{t('next_steps')}</h2>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {stepKeys.map((step, i) => (
              <motion.div key={step.num} initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ duration: 0.5, delay: i * 0.1 }} className="text-center">
                <div className="w-12 h-12 rounded-full bg-gold text-navy font-display font-bold text-xl flex items-center justify-center mx-auto mb-4">{step.num}</div>
                <h3 className="font-medium text-navy mb-2">{t(step.title)}</h3>
                <p className="text-sm text-slate">{t(step.desc)}</p>
              </motion.div>
            ))}
          </div>
        </Container>
      </section>
    </div>
  );
}
