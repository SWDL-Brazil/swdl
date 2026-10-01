'use client';

import Link from 'next/link';
import { useTranslations } from 'next-intl';
import { Mail, Instagram, ExternalLink } from 'lucide-react';
import { LanguageSwitcher } from './LanguageSwitcher';
import { ColorblindToggle } from '@/components/a11y/ColorblindToggle';

const SWDL_CONFIG = {
  email: 'pedro.pereira63@portalsesisp.org.br',
  siteUrl: 'https://swdl-5a3fa.web.app',
};

const footerLinks = [
  { key: 'home', href: '/' },
  { key: 'noticias', href: '/noticias' },
  { key: 'comites', href: '/comites' },
  { key: 'agenda', href: '/agenda' },
  { key: 'certificado', href: '/certificado' },
  { key: 'sobre', href: '/sobre' },
  { key: 'faca_parte', href: '/faca-parte' },
];

const legalLinks = [
  { key: 'aviso_legal', href: '/aviso-legal' },
  { key: 'privacidade', href: '/privacidade' },
  { key: 'termos', href: '/termos' },
];

export function Footer() {
  const t = useTranslations('footer');

  return (
    <footer className="bg-navy-dark text-white pt-16 pb-8">
      <div className="container">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          {/* Brand */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-3 mb-4">
              <img
                src="/img/logo.png"
                alt="SWDL Logo"
                className="h-[48px] w-auto object-contain"
              />
              <span className="font-display text-3xl font-bold tracking-tight">
                SW<span className="text-gold">DL</span>
              </span>
            </div>
            <p className="text-slate-light text-sm leading-relaxed max-w-sm mb-4">
              {t('description')}
            </p>
            <p className="text-slate-light text-xs mb-6 opacity-90">
              {t('address')}
            </p>
            <div className="flex items-center gap-4">
              <a
                href={`mailto:${SWDL_CONFIG.email}`}
                className="flex items-center gap-2 text-slate-light text-sm hover:text-gold transition-colors"
              >
                <Mail size={16} />
                {t('contact')}
              </a>
              <a
                href="https://instagram.com/swdl.brazil"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-slate-light text-sm hover:text-gold transition-colors"
              >
                <Instagram size={16} />
                @swdl.brazil
              </a>
            </div>
          </div>

          {/* Links */}
          <div>
            <h4 className="font-mono text-xs tracking-widest uppercase text-gold mb-4">
              {t('navigation')}
            </h4>
            <ul className="list-none space-y-2">
              {footerLinks.map((link) => (
                <li key={link.key}>
                  <Link
                    href={link.href}
                    className="text-slate-light text-sm hover:text-white transition-colors no-underline"
                  >
                    {t(`links.${link.key}`)}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="font-mono text-xs tracking-widest uppercase text-gold mb-4">
              {t('legal')}
            </h4>
            <ul className="list-none space-y-2">
              {legalLinks.map((link) => (
                <li key={link.key}>
                  <Link
                    href={link.href}
                    className="text-slate-light text-sm hover:text-white transition-colors no-underline"
                  >
                    {t(`links.${link.key}`)}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Language selector + accessibility */}
        <div className="border-b border-white/7 pb-5 mb-5 flex flex-wrap items-center gap-4 justify-between">
          <LanguageSwitcher />
          <ColorblindToggle />
        </div>

        {/* Bottom bar */}
        <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-slate-light text-xs opacity-90">
            © {new Date().getFullYear()} SESI World Diplomacy League — {t('developed_by')}
          </p>
          <div className="flex items-center gap-6">
            <a
              href="https://github.com/SWDL-Brazil"
              target="_blank"
              rel="noopener noreferrer"
              className="text-slate-light text-xs hover:text-gold transition-colors flex items-center gap-1"
            >
              GitHub <ExternalLink size={12} />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
