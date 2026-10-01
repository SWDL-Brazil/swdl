export type AgendaStatus =
  | 'done'
  | 'now'
  | 'next'
  | 'break'
  | 'vote'
  | 'crisis'
  | 'award'
  | 'archive'
  | string;

export interface StatusMeta {
  cls: 'past' | 'current' | 'future' | 'archive';
  tagKey: string;
  tagCls: string;
}

export const STATUS_CONFIG: Record<string, StatusMeta> = {
  done: { cls: 'past', tagKey: 'status_done', tagCls: 'tag-done' },
  now: { cls: 'current', tagKey: 'status_now', tagCls: 'tag-now' },
  next: { cls: 'future', tagKey: 'status_next', tagCls: 'tag-next' },
  break: { cls: 'future', tagKey: 'status_break', tagCls: 'tag-break' },
  vote: { cls: 'current', tagKey: 'status_vote', tagCls: 'tag-vote' },
  crisis: { cls: 'current', tagKey: 'status_crisis', tagCls: 'tag-crisis' },
  award: { cls: 'future', tagKey: 'status_award', tagCls: 'tag-award' },
  archive: { cls: 'archive', tagKey: 'status_archive', tagCls: 'tag-archive' },
};

export const DEFAULT_STATUS: StatusMeta = STATUS_CONFIG.next;

export const PERIOD_COLORS: Record<string, string> = {
  navy: '#0D1B2A',
  gold: '#7A5F1F',
  green: '#15803D',
  blue: '#1D4ED8',
  red: '#B91C1C',
  slate: '#5A6170',
};

export function statusMeta(status: string): StatusMeta {
  return STATUS_CONFIG[status] || DEFAULT_STATUS;
}

export function periodColor(color?: string): string {
  return PERIOD_COLORS[color || ''] || PERIOD_COLORS.slate;
}
