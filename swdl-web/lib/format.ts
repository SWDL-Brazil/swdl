const UNITS: [Intl.RelativeTimeFormatUnit, number][] = [
  ['year', 31536000],
  ['month', 2592000],
  ['week', 604800],
  ['day', 86400],
  ['hour', 3600],
  ['minute', 60],
];

export function formatTimeAgo(
  createdAt?: string | null,
  locale = 'pt-BR',
  fallback?: string
): string | undefined {
  if (!createdAt) return fallback;
  const date = new Date(createdAt);
  if (Number.isNaN(date.getTime())) return fallback;

  const diffSec = Math.floor((date.getTime() - Date.now()) / 1000);
  const abs = Math.abs(diffSec);

  if (abs < 60) {
    try {
      return new Intl.RelativeTimeFormat(locale, { numeric: 'auto' }).format(
        diffSec,
        'minute'
      );
    } catch {
      return fallback;
    }
  }

  for (const [unit, secs] of UNITS) {
    if (abs >= secs) {
      const value = Math.trunc(diffSec / secs);
      try {
        return new Intl.RelativeTimeFormat(locale, { numeric: 'auto' }).format(
          value,
          unit
        );
      } catch {
        return fallback;
      }
    }
  }

  try {
    return date.toLocaleDateString(locale, {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return fallback;
  }
}

const CATEGORY_KEYS = new Set([
  'geral',
  'oficial',
  'imprensa',
  'crise',
  'votacao',
]);

export function categoryLabelKey(slug?: string): string | null {
  if (!slug || !CATEGORY_KEYS.has(slug)) return null;
  return `category_${slug}`;
}

export function committeeStatusKey(statusType?: string): string | null {
  if (!statusType) return null;
  if (['voting', 'debate', 'waiting', 'done'].includes(statusType)) {
    return `status_${statusType}`;
  }
  return null;
}
