'use client';

import { useEffect, useState } from 'react';
import { useTranslations } from 'next-intl';
import { motion } from 'motion/react';
import { api, CommitteeStatus } from '@/lib/api';
import { Card } from '@/components/ui/Card';
import { CommitteeDot } from '@/components/ui/Badge';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

const committeeIcons: Record<string, string> = {
  'Conselho de Segurança': '/icons/shield.svg',
  'Comissão de Meio Ambiente': '/icons/leaf.svg',
  'Direitos Humanos': '/icons/scales.svg',
  'ECOSOC': '/icons/coins.svg',
  'DISEC': '/icons/lock.svg',
  'OMS': '/icons/hospital.svg',
  'ACNUR': '/icons/dove.svg',
  'UNESCO': '/icons/books.svg',
};

const staticCommittees = [
  { key: 'guide', icon: '/icons/graduation.svg' },
  { key: 'mma', icon: '/icons/leaf.svg' },
  { key: 'dhr', icon: '/icons/scales.svg' },
  { key: 'ecosoc', icon: '/icons/coins.svg' },
  { key: 'disec', icon: '/icons/lock.svg' },
  { key: 'oms', icon: '/icons/hospital.svg' },
  { key: 'acnur', icon: '/icons/dove.svg' },
] as const;

export function CommitteesPreview() {
  const t = useTranslations('home');
  const tc = useTranslations('home.committee_preview');
  const [committees, setCommittees] = useState<CommitteeStatus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadComites() {
      const data = await api.comites();
      if (data) setCommittees(data);
      setLoading(false);
    }
    loadComites();
  }, []);

  return (
    <section className="py-20 bg-navy">
      <div className="container">
        <div className="text-center mb-12">
          <span className="section-label justify-center text-gold">
            <span className="w-7 h-px bg-gold" />
            {t('committees_label')}
          </span>
          <h2 className="section-title text-white">{t('committees_title')}</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {staticCommittees.map((committee, i) => {
            const name = tc(`${committee.key}.name`);
            return (
            <motion.div
              key={committee.key}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
            >
              <Card className="bg-navy-mid/50 border-white/10 hover:bg-navy-mid transition-all duration-300 hover:shadow-glow h-full">
                <div className="flex items-start gap-3">
                  <img
                    src={committee.icon}
                    alt={name}
                    className="w-10 h-10 object-contain opacity-80 mt-7"
                  />
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-white text-sm mb-1">
                      {name}
                    </h3>
                    <span className="text-[0.72rem] font-mono text-gold/70 tracking-wider uppercase">
                      {tc(`${committee.key}.tag`)}
                    </span>
                    <p className="text-xs text-slate-light mt-2 line-clamp-2">
                      {tc(`${committee.key}.desc`)}
                    </p>
                  </div>
                </div>
              </Card>
            </motion.div>
            );
          })}
        </div>

        <div className="text-center mt-8">
          <Link
            href="/comites"
            className="inline-flex items-center gap-2 text-gold text-sm font-medium hover:text-gold-light transition-colors no-underline"
          >
            {t('committees_all')} <ArrowRight size={16} />
          </Link>
        </div>
      </div>
    </section>
  );
}
