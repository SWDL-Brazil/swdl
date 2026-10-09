import { cn } from '@/lib/utils';
import { committeeColorVar, normalizeCommittee } from '@/lib/committee-colors';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'crise' | 'oficial' | 'imprensa' | 'votacao' | 'default';
  className?: string;
}

const variantClass: Record<string, string> = {
  crise: 'badge-crise',
  oficial: 'badge-oficial',
  imprensa: 'badge-imprensa',
  votacao: 'badge-votacao',
  default: 'badge-default',
};

export function Badge({ children, variant = 'default', className }: BadgeProps) {
  return (
    <span className={cn('badge', variantClass[variant], className)}>{children}</span>
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
  const normalized = normalizeCommittee(committee);
  const code = shortCodeFor(normalized, committee);

  return (
    <span
      className={cn('inline-flex items-center justify-center w-2 h-2 rounded-full shrink-0 cvd-dot committee-dot', className)}
      style={{ '--dot-color': committeeColorVar(committee) } as React.CSSProperties}
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
