// O bundle de produção já foi gerado com `process.env.NEXT_PUBLIC_API_URL`
// resolvendo para a string literal "NEXT_PUBLIC_API_URL" (env ausente/errada no
// build), o que quebrava TODOS os fetches: a URL virava relativa
// (/NEXT_PUBLIC_API_URL/agenda -> 404). Por isso o valor só é aceito se for
// uma URL http(s) de verdade; caso contrário caímos no endpoint de produção.
const FALLBACK_API_BASE = 'https://swdl.onrender.com/api';

const RAW_API_BASE: string =
  (typeof process !== 'undefined' && process.env && process.env.NEXT_PUBLIC_API_URL) || '';

const API_BASE = /^https?:\/\/\S+$/i.test(RAW_API_BASE.trim())
  ? RAW_API_BASE.trim().replace(/\/+$/, '')
  : FALLBACK_API_BASE;

// Em dev, permite fallback local se a env não estavar no build do browser
const API_BASE_CANDIDATES = [
  API_BASE,
  ...(process.env.NODE_ENV === 'development' ? ['http://localhost:5000/api'] : []),
].filter((v, i, a) => a.indexOf(v) === i);

// Origem do backend Flask (sem o sufixo /api) — usado para links diretos
// como o PDF público /certificado/<code>.
export const BACKEND_ORIGIN = API_BASE.replace(/\/api\/?$/, '');

// Assets com path relativo (ex.: /api/uploads/news/... vindo do backend)
// precisam da origem do Flask: no Vercel/Firebase o browser resolveria
// contra o domínio atual e daria 404.
export function resolveAssetUrl(url?: string | null): string {
  if (!url) return '';
  if (/^https?:\/\//i.test(url)) return url;
  if (url.startsWith('/')) return `${BACKEND_ORIGIN}${url}`;
  return url;
}

export interface News {
  id: number;
  title: string;
  slug: string;
  excerpt?: string;
  body?: string;
  category: string;
  category_slug: string;
  category_icon: string;
  committee: string;
  is_crisis: boolean;
  image_url: string;
  time_ago: string;
  created_at: string;
  tags?: string[];
  author?: string;
  related?: NewsMini[];
}

export interface NewsMini {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  category: string;
  category_slug: string;
  category_icon: string;
  committee: string;
  is_crisis: boolean;
  image_url: string;
  time_ago: string;
  created_at: string | null;
}

export interface AgendaItem {
  id: number;
  title: string;
  description: string;
  day: number;
  order: number;
  event_date: string;
  start_time: string;
  end_time: string;
  committee: string;
  location: string;
  status: string;
  period_id: number | null;
  period_name: string;
}

export interface EventPeriod {
  id: number;
  name: string;
  start_date: string;
  end_date: string;
  order: number;
  color: string;
}

export interface TickerItem {
  type: string;
  html: string;
  text: string;
  priority: number;
}

export interface CommitteeStatus {
  id: number;
  name: string;
  image: string;
  status_label: string;
  status_type: string;
  next_time: string;
  next_title: string;
}

export interface EventConfig {
  inscricoes_abertas: boolean;
  phase: string;
}

export interface CrisisStatus {
  crisis_active: boolean;
  crisis_message: string | null;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  icon: string;
}

export interface CertificateResult {
  ok: boolean;
  valid: boolean;
  name: string;
  verification_code: string | null;
  pdf_path: string | null;
  digital_signature: boolean;
  signature_valid: boolean | null;
  signed_at: string | null;
  global_id: string | null;
  country: string;
  country_flag: string;
  committee: string;
  committee_name: string;
}

export type CertificateLookup =
  | { status: 'valid'; data: CertificateResult }
  | { status: 'not_found' }
  | { status: 'error' };

export interface RegistrationData {
  name: string;
  email: string;
  phone: string;
  instagram?: string;
  school?: string;
  grade?: string;
  experience?: string;
  interests?: string;
  motivation?: string;
  type: string;
  formato?: string;
  members?: Array<{
    name: string;
    email: string;
    phone: string;
    instagram: string;
    grade?: string;
    motivation?: string;
  }>;
  accept_terms: boolean;
}

async function fetchJSON<T>(endpoint: string, params?: Record<string, string | number | undefined>): Promise<T | null> {
  const qs = params
    ? '?' + Object.entries(params)
        .filter(([, v]) => v !== undefined && v !== null && v !== '')
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
        .join('&')
    : '';

  let lastStatus = 0;
  for (const base of API_BASE_CANDIDATES) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 10000);
      const response = await fetch(`${base}${endpoint}${qs}`, {
        signal: controller.signal,
        next: { revalidate: 60 },
      });
      clearTimeout(timeout);
      lastStatus = response.status;
      if (response.ok) return response.json() as Promise<T>;
    } catch {
      // tenta próximo base
    }
  }
  if (lastStatus) console.warn(`API Error: ${endpoint} returned ${lastStatus}`);
  return null;
}

async function fetchAPI<T>(endpoint: string, params?: Record<string, string | number | undefined>): Promise<T | null> {
  return fetchJSON<T>(endpoint, params);
}

export const api = {
  noticias: (params?: { category?: string; committee?: string; limit?: number }) =>
    fetchAPI<News[]>('/noticias', params),

  noticia: (slug: string) =>
    fetchAPI<News>(`/noticia-json/${slug}`),

  categorias: () =>
    fetchAPI<Category[]>('/categorias'),

  agenda: (params?: { limit?: number; day?: number }) =>
    fetchAPI<AgendaItem[]>('/agenda', params),

  agendaAgora: () =>
    fetchAPI<{ current: AgendaItem | null; next: AgendaItem | null }>('/agenda/agora'),

  periods: () =>
    fetchAPI<EventPeriod[]>('/periods'),

  comites: () =>
    fetchAPI<CommitteeStatus[]>('/comites'),

  ticker: () =>
    fetchAPI<TickerItem[]>('/ticker'),

  status: () =>
    fetchAPI<CrisisStatus>('/status'),

  config: () =>
    fetchAPI<EventConfig>('/config'),

  bandeira: (country: string) =>
    fetchAPI<{ ok: boolean; flag_url: string; name: string; code: string }>('/bandeira', { country }),

  // Fetch próprio: precisa distinguir 404 (certificado não encontrado)
  // de falha de rede — o fetchJSON devolve null e engole o status.
  certificado: async (code: string): Promise<CertificateLookup> => {
    for (const base of API_BASE_CANDIDATES) {
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 10000);
        const response = await fetch(
          `${base}/certificado/validar?code=${encodeURIComponent(code)}`,
          { signal: controller.signal }
        );
        clearTimeout(timeout);
        if (response.ok) {
          return { status: 'valid', data: (await response.json()) as CertificateResult };
        }
        if (response.status === 404) return { status: 'not_found' };
        if (response.status >= 500) continue; // tenta próximo base
        return { status: 'error' };
      } catch {
        // rede/timeout — tenta próximo base
      }
    }
    return { status: 'error' };
  },

  inscrever: async (data: RegistrationData) => {
    try {
      const response = await fetch(`${API_BASE}/inscricao`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      return response.json();
    } catch (error) {
      console.warn('Registration error:', error);
      return { ok: false, error: 'Network error' };
    }
  },
};
