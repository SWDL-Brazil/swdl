import { cn } from '@/lib/utils';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'crise' | 'oficial' | 'imprensa' | 'votacao' | 'default';
  className?: string;
}

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 font-mono text-[0.68rem] font-medium tracking-[0.1em] uppercase px-2.5 py-1 rounded-sm text-white',
        variant === 'crise' && 'bg-red-700',
        variant === 'oficial' && 'bg-blue-800',
        variant === 'imprensa' && 'bg-emerald-800',
        variant === 'votacao' && 'bg-navy',
        variant === 'default' && 'bg-slate-dark',
        className
      )}
    >
      {children}
    </span>
  );
}

interface CommitteeDotProps {
  committee: string;
  className?: string;
}

const shortCodes: Record<string, string> = {
  cs: 'CS',
  'conselho de seguranca': 'CS',
  mma: 'MMA',
  'meio ambiente': 'MA',
  'comissao de meio ambiente': 'MA',
  dhr: 'DH',
  'direitos humanos': 'DH',
  ecosoc: 'EC',
  disec: 'DI',
  oms: 'OM',
  acnur: 'AC',
  unesco: 'UN',
  canabis: 'CB',
  misoginia: 'MG',
  escravidao: 'ES',
  ormuz: 'HZ',
};

function shortCodeFor(normalized: string, committee: string): string {
  const hit = shortCodes[normalized] || Object.entries(shortCodes).find(([key]) => normalized.includes(key))?.[1];
  if (hit) return hit;
  const words = committee.trim().split(/\s+/);
  if (words.length > 1) {
    return words.map((w) => w[0]).join('').toUpperCase().slice(0, 3);
  }
  return committee.slice(0, 3).toUpperCase();
}

export function CommitteeDot({ committee, className }: CommitteeDotProps) {
  const normalized = committee
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim();

  const colorMap: Record<string, string> = {
    cs: 'bg-red-700',
    'conselho de seguranca': 'bg-red-700',
    mma: 'bg-emerald-800',
    'meio ambiente': 'bg-emerald-800',
    'comissao de meio ambiente': 'bg-emerald-800',
    dhr: 'bg-purple-700',
    'direitos humanos': 'bg-purple-700',
    ecosoc: 'bg-amber-700',
    disec: 'bg-orange-700',
    oms: 'bg-blue-700',
    acnur: 'bg-sky-700',
    unesco: 'bg-indigo-700',
    canabis: 'bg-green-800',
    misoginia: 'bg-fuchsia-700',
    escravidao: 'bg-amber-800',
    ormuz: 'bg-cyan-700',
  };

  const matched =
    colorMap[normalized] ||
    Object.entries(colorMap).find(([key]) => normalized.includes(key))?.[1];

  const code = shortCodeFor(normalized, committee);

  return (
    <span
      className={cn(
        'inline-flex items-center justify-center w-2 h-2 rounded-full shrink-0 cvd-dot',
        matched || 'bg-slate-dark',
        className
      )}
      role="img"
      aria-label={committee}
      title={committee}
    >
      <span className="cvd-dot-code" aria-hidden="true">
        {code}
      </span>
    </span>
  );
}
