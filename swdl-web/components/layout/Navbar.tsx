'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { Menu, X } from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { key: 'home', href: '/' },
  { key: 'noticias', href: '/noticias' },
  { key: 'comites', href: '/comites' },
  { key: 'agenda', href: '/agenda' },
  { key: 'certificado', href: '/certificado' },
  { key: 'sobre', href: '/sobre' },
];

export function Navbar() {
  const t = useTranslations('nav');
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 40);
    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const isActive = (href: string) => {
    const path = pathname.replace(/^\/[a-z]{2}(-[A-Z]{2})?/, '') || '/';
    if (href === '/') return path === '/';
    return path.startsWith(href);
  };

  return (
    <nav
      className={cn(
        'fixed top-0 left-0 right-0 z-50 h-[68px] flex items-center justify-between px-6 md:px-12 transition-all duration-300',
        scrolled
          ? 'bg-white/95 backdrop-blur-xl border-b border-navy/10 shadow-md shadow-navy/5'
          : 'bg-navy/95 backdrop-blur-xl border-b border-gold/20',
        scrolled && !mobileOpen && 'shadow-md shadow-navy/5'
      )}
    >
      <Link href="/" className="flex items-center">
        <div className="h-[52px] md:h-[60px] flex items-center gap-2">
          <img
            src="/img/logo.png"
            alt="SWDL Logo"
            className="h-full w-auto object-contain"
          />
        </div>
      </Link>

      <ul className="hidden md:flex items-center gap-7 list-none">
        {navItems.map((item) => (
          <li key={item.key}>
            <Link
              href={item.href}
              className={cn(
                'text-xs font-medium tracking-wide uppercase no-underline pb-0.5 relative transition-colors duration-200',
                scrolled
                  ? isActive(item.href)
                    ? 'text-navy font-semibold'
                    : 'text-navy/70 hover:text-navy'
                  : isActive(item.href)
                    ? 'text-white'
                    : 'text-slate-light hover:text-white'
              )}
            >
              {t(item.key)}
              <span
                className={cn(
                  'absolute bottom-[-4px] left-0 right-0 h-px bg-gold transition-transform duration-250 origin-left',
                  isActive(item.href) ? 'scale-x-100' : 'scale-x-0 hover:scale-x-100'
                )}
              />
            </Link>
          </li>
        ))}
        <li>
          <Link
            href="/faca-parte"
            className="bg-gold text-navy px-5 py-2 rounded text-xs font-bold tracking-wide uppercase no-underline transition-all duration-200 hover:-translate-y-0.5 hover:shadow-glow"
          >
            {t('faca_parte')}
          </Link>
        </li>
      </ul>

      <button
        className={cn(
          'md:hidden p-2 bg-transparent border-none cursor-pointer transition-colors',
          scrolled ? 'text-navy' : 'text-white'
        )}
        onClick={() => setMobileOpen(!mobileOpen)}
        aria-label="Menu"
      >
        {mobileOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {mobileOpen && (
        <div className="fixed inset-0 top-[68px] bg-navy/98 backdrop-blur-xl z-40 md:hidden">
          <ul className="flex flex-col items-center gap-8 pt-12 list-none">
            {navItems.map((item) => (
              <li key={item.key}>
                <Link
                  href={item.href}
                  className={cn(
                    'text-lg font-medium tracking-wide uppercase no-underline',
                    isActive(item.href) ? 'text-gold' : 'text-white'
                  )}
                  onClick={() => setMobileOpen(false)}
                >
                  {t(item.key)}
                </Link>
              </li>
            ))}
            <li>
              <Link
                href="/faca-parte"
                className="bg-gold text-navy px-8 py-3 rounded text-sm font-bold tracking-wide uppercase no-underline"
                onClick={() => setMobileOpen(false)}
              >
                {t('faca_parte')}
              </Link>
            </li>
          </ul>
        </div>
      )}
    </nav>
  );
}
