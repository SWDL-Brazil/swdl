'use client';

import { useTranslations } from 'next-intl';
import { motion } from 'motion/react';
import { Globe, Users, Award, Calendar } from 'lucide-react';

const stats = [
  {
    icon: Globe,
    value: '193',
    labelKey: 'stats_countries',
    descriptionKey: 'stats_countries_desc',
  },
  {
    icon: Users,
    value: '216',
    labelKey: 'stats_delegates',
    descriptionKey: 'stats_delegates_desc',
  },
  {
    icon: Award,
    value: '8',
    labelKey: 'stats_committees',
    descriptionKey: 'stats_committees_desc',
  },
  {
    icon: Calendar,
    value: '8',
    labelKey: 'stats_editions',
    descriptionKey: 'stats_editions_desc',
  },
];

export function Stats() {
  const t = useTranslations('home');

  return (
    <section className="py-20 bg-white">
      <div className="container">
        <div className="text-center mb-12">
          <span className="section-label justify-center">
            <span className="w-7 h-px bg-gold" />
            {t('stats_label')}
          </span>
          <h2 className="section-title">{t('stats_title')}</h2>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((stat, i) => (
            <motion.div
              key={stat.value}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-50px' }}
              transition={{ duration: 0.6, delay: i * 0.1 }}
              className="text-center p-6 rounded-lg bg-surface border border-navy/5 hover:shadow-elevated transition-all duration-300"
            >
              <div className="w-12 h-12 rounded-full bg-gold/10 flex items-center justify-center mx-auto mb-4">
                <stat.icon className="w-6 h-6 text-gold-dark" />
              </div>
              <span className="block text-4xl font-display font-bold text-navy mb-1">
                {stat.value}
              </span>
              <span className="block text-sm font-medium text-navy mb-1">
                {t(stat.labelKey)}
              </span>
              <span className="block text-xs text-slate">
                {t(stat.descriptionKey)}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
