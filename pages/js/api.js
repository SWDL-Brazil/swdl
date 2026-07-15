/* ============================================================
   SWDL — api.js
   Cliente central para consumir o backend Flask
   Base URL aponta para o servidor local em desenvolvimento.
   Em produção, troque pela URL do servidor real.
   ============================================================ */

// Aponta para o Render em produção, local em desenvolvimento
const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:5000/api'
  : 'https://swdl.onrender.com/api';

const SWDL_API = {

  // ── GET genérico ──────────────────────────────────────────
  async get(endpoint, params = {}) {
    const url = new URL(API_BASE + endpoint);
    Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v));
    try {
      const res = await fetch(url.toString());
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return await res.json();
    } catch (err) {
      console.warn(`[SWDL API] GET ${endpoint} falhou:`, err.message);
      return null;
    }
  },

  // ── POST genérico ─────────────────────────────────────────
  async post(endpoint, data = {}) {
    try {
      const res = await fetch(API_BASE + endpoint, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(data),
      });
      return await res.json();
    } catch (err) {
      console.warn(`[SWDL API] POST ${endpoint} falhou:`, err.message);
      return null;
    }
  },

  // ── Atalhos específicos ───────────────────────────────────
  noticias:  (params) => SWDL_API.get('/noticias', params),
  agenda:    (params) => SWDL_API.get('/agenda',   params),
  agendaAgora:()      => SWDL_API.get('/agenda/agora'),
  status:    ()       => SWDL_API.get('/status'),
  inscrever: (data)   => SWDL_API.post('/inscricao', data),
  config:    ()       => SWDL_API.get('/config'),
};