// Cores de comitê como tokens CSS (--committee-*). O valor final (normal vs
// daltônico) é resolvido pelo CSS conforme [data-cvd], então basta consumir
// a var — sem hex hardcoded nos componentes.

const VAR_BY_KEY: Record<string, string> = {
  cs: 'cs',
  'conselho de seguranca': 'cs',
  mma: 'mma',
  'meio ambiente': 'mma',
  'comissao de meio ambiente': 'mma',
  dhr: 'dhr',
  'direitos humanos': 'dhr',
  ecosoc: 'ecosoc',
  disec: 'disec',
  oms: 'oms',
  acnur: 'acnur',
  unesco: 'unesco',
  canabis: 'canabis',
  misoginia: 'misoginia',
  escravidao: 'escravidao',
  ormuz: 'ormuz',
};

export function normalizeCommittee(name: string): string {
  return name
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .trim();
}

export function committeeColorVar(committee: string): string {
  const n = normalizeCommittee(committee);
  const key =
    VAR_BY_KEY[n] ||
    Object.entries(VAR_BY_KEY).find(([k]) => n.includes(k))?.[1];
  return key ? `var(--committee-${key})` : 'var(--period-muted)';
}
