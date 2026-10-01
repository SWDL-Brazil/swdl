'use client';

import { useEffect, useRef, useState } from 'react';
import { useLocale } from 'next-intl';
import { usePathname, useRouter } from 'next/navigation';
import { ChevronDown } from 'lucide-react';
import { cn } from '@/lib/utils';

export const LOCALES = [
  { code: 'pt-BR', label: 'Português (Brasil)', flag: '🇧🇷' },
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'es', label: 'Español', flag: '🇪🇸' },
  { code: 'fr', label: 'Français', flag: '🇫🇷' },
  { code: 'de', label: 'Deutsch', flag: '🇩🇪' },
  { code: 'it', label: 'Italiano', flag: '🇮🇹' },
  { code: 'nl', label: 'Nederlands', flag: '🇳🇱' },
  { code: 'id', label: 'Bahasa Indonesia', flag: '🇮🇩' },
  { code: 'ms', label: 'Bahasa Melayu', flag: '🇲🇾' },
] as const;

interface LanguageSwitcherProps {
  align?: 'left' | 'right';
  className?: string;
  variant?: 'dark' | 'light';
}

export function LanguageSwitcher({ align = 'left', className, variant = 'dark' }: LanguageSwitcherProps) {
  const locale = useLocale();
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  const current = LOCALES.find((l) => l.code === locale) || LOCALES[0];

  useEffect(() => {
    if (!open) return;
    const onDoc = (e: MouseEvent) => {
      if (rootRef.current && !rootRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', onDoc);
    return () => document.removeEventListener('mousedown', onDoc);
  }, [open]);

  const switchTo = (code: string) => {
    setOpen(false);
    if (code === locale) return;
    document.cookie = `swdl_lang=${code};path=/;max-age=31536000;samesite=lax`;
    const stripped = pathname.replace(/^\/[^/]+/, '') || '';
    router.push(`/${code}${stripped}`);
    router.refresh();
  };

  return (
    <div ref={rootRef} className={cn('relative inline-block text-left', className)}>
      <button
        type="button"
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label="Idioma / Language"
        onClick={() => setOpen((v) => !v)}
        className={cn(
          'inline-flex items-center gap-2 rounded border px-3 py-1.5 text-[12px] transition-colors font-body',
          variant === 'light'
            ? 'border-navy/15 bg-white/70 text-navy hover:bg-white hover:border-navy/30'
            : 'border-white/12 bg-white/5 text-white hover:bg-white/10 hover:border-white/25'
        )}
      >
        <span aria-hidden>{current.flag}</span>
        <span className="hidden sm:inline">{current.label}</span>
        <span className="sm:hidden">{current.code}</span>
        <ChevronDown
          size={14}
          className={cn('transition-transform', open && 'rotate-180')}
        />
      </button>

      {open && (
        <ul
          role="listbox"
          className={cn(
            'absolute bottom-full mb-2 z-50 min-w-[220px] rounded-md border p-1.5 shadow-[0_8px_32px_rgba(0,0,0,0.5)]',
            variant === 'light'
              ? 'border-navy/10 bg-white text-navy'
              : 'border-white/10 bg-[#0F1A2E]',
            align === 'right' ? 'right-0' : 'left-0'
          )}
        >
          {LOCALES.map((lang) => {
            const active = lang.code === locale;
            return (
              <li key={lang.code}>
                <button
                  type="button"
                  role="option"
                  aria-selected={active}
                  onClick={() => switchTo(lang.code)}
                  className={cn(
                    'block w-full rounded px-3 py-2 text-left text-[13px] transition-colors',
                    active
                      ? variant === 'light'
                        ? 'bg-gold/10 text-[#7a5f1f]'
                        : 'bg-gold/10 text-gold'
                      : variant === 'light'
                        ? 'text-[#5a6170] hover:bg-navy/5 hover:text-navy'
                        : 'text-slate-light hover:bg-white/6 hover:text-white'
                  )}
                >
                  {lang.flag} {lang.label}
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
