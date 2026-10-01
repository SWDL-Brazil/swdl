# SWDL — Session Summary

## Objective
Build a complete student panel + admin backend for the SWDL Model UN platform with agenda-based auto-locking, per-student certificate signing/release, and no manual phase switching.

---

## Completed

### Student Panel
- "Meu Debate" highlight card on dashboard when delegation assigned
- DPO deadline check (3 days before 1st agenda item)
- Voting auto-unlock on event day (`is_event_day` flag)
- Certificates: compile/release é manual pelo admin (ver Admin Panel)
- Student certificates page listing released certificates

### Admin Panel
- **Admin routes**: pacote `backend/routes/admin/` (20 submódulos, blueprint `admin_bp` em `_helpers.py`)
- **DPO Management**: List, download, delete DPOs (resets so student can re-upload)
- **Delegation Create Form**: Theme + Country + Student selection (1 to 4+ students)
  -- Creates Inscription, User (login), ParticipationHistory automatically
- **Certificates (fluxo atual — o sistema de templates PDF foi REMOVIDO no commit `b7ec9fc`; liberação/assinatura manuais REMOVIDAS da admin)**:
  -- Gerar códigos de verificação (por aluno ou em lote) → upload de PDF por aluno (libera o certificado no painel do delegado; remover PDF revoga a liberação)
  -- `certificate_view` (`/certificado/<code>`) serve o PDF ou a página do certificado

### Admin — Agenda (correções)
- `get_resolved_phase()` em `agenda_utils.py`: fase = agenda (ou `'pre'`) + override manual — fonte única para context processor e dashboards (corrige dashboard `/admin/` vazio com fase `None` e switcher 🟢/🔴/🔵 ignorado em `/admin/` e `/admin/diretor`)
- `get_current_next()`: "Agora/Próximo" derivado do horário (status `now/next` nunca era gravado no banco) — card AO VIVO dos dashboards, card "Agora" do aluno e `/api/agenda/agora` voltaram a funcionar
- Edit não zera mais o `order` (preserva drag-and-drop); create insere no fim do grupo (`_next_order`)
- Form: sigla de comitê (`CS`, `DHR`...) e `day > 10` não são mais apagados ao editar
- Reorder em 1 query (era N+1 ≈ 180 ms/item), payload validado, `fetch` com rollback visual no erro
- Validação de data/hora no create/edit (evita fase `None` silenciosa)
- Switcher de fase e links Agenda/Períodos só para admin (diretor levava 403)
- Limpeza: `get_agenda_bounds`, `_cached_phase_override`, imports mortos removidos
- `backend/test_agenda.py`: 19 checagens funcionais (roda junto com `test_perf_pages.py`)

### Infrastructure
- `datetime.utcnow` replaced with `datetime.now(timezone.utc)` everywhere
- Hardcoded email and year removed from templates
- CSS extracted to external file `student.css`
- Manual phase system removed → `get_agenda_status()` driven by agenda items
- Added database indexes on all frequently queried columns
- Removed `available_themes` from context_processor (was running on every page)
- Consolidated dashboard COUNT queries (20→3)

### Deploy
- Hosted on Render via GitHub (`SWDL-Brazil/swdl.git`)
- Auto-deploys on push to main
- Bug fix: `url_for('certificate_view')` → `url_for('vote.certificate_view')` (missing blueprint prefix)

### Public Site (pages/)
- Crisis banner rewritten: `position: fixed; top:68px; z-index:100` + `body.crisis-active .ticker-bar { margin-top:40px }` — não sobrepõe o ticker
- Lógica do crisis banner removida do `main.js` → cada página tem seu próprio `loadCrisisBanner()` inline
- Banner recarrega a cada 60s (junto com ticker/notícias/agenda)
- Botão ✕ apenas oculta (não destrói permanentemente); próxima poll re-exibe se crise ativa
- Implementado em todas as 9 páginas públicas com `#crisis-banner`: index, noticias, comites, agenda, sobre, faca-parte, aviso-legal, privacidade, termos

### Next.js Portal (swdl-web/)
- **Portal de Notícias** redesenhado inspirado no template Morning + BBC:
  - `.container-portal` 1336px, `.section-rule` (borda 4px superior), fontes SWDL (Playfair/DM Sans), paleta navy/gold
  - Sub-bar sticky: categorias + abas comitê + busca client-side
  - Hero 75/25: LeadStory + TopStories | HeroSidebar sticky
  - Seções: CrisisFeed (se crise), CommitteeSections, ArchiveList + NewsSidebar sticky (desktop)
  - Filtro via query string `?cat=&committee=` com `useSearchParams` + Suspense
- **Rota de artigo**: `app/[locale]/noticia/[slug]/page.tsx` (resolve link faltante do NewsGrid)
- **API Flask**: `GET /api/noticia-json/<slug>` retorna JSON + `related[]` (o `/noticia/<slug>` continua servindo HTML)
- **Ticker**: prioriza `type === 'urgent'` e mostra `🚨 N ALERTAS` quando houver
- **i18n**: namespaces `noticias.*` (portal) e `noticia.*` em 9 idiomas
- **`.gitignore`**: `.next/` e `swdl-web/.next/` adicionados
- `npm run build` passando (typecheck incluso; `next lint` sem config ESLint)

### Performance — Fase 0 (medição) + Fase 1 (otimizações)
- **Causa raiz confirmada**: `srv ≈ db` em toda rota → cada round-trip ao banco custa **~180 ms** (rede/DB); o app em si é rápido. `api/status` (1 query) = 353 ms.
- Instrumentação em `backend/app.py::_setup_perf`: headers `X-Request-Time`, `X-Query-Count`, `X-Query-Time`, log `SLOW` (≥`PERF_SLOW_MS`) e `DB target:` no boot (mostra host do DB — usado para checar região).
- Sonda de produção: `backend/perf_probe.py --runs N [--only a,b] [--base URL]` (login automático; TTFB/total/srv/db/queries por rota).
- Harness local: `backend/test_perf_pages.py --real` (copia de `backend/swdl.db`, 18 rotas, CSRF off) — todas retornam 200.
- **Fase 1 aplicada** (commits `426e1ee`, `5de10a6`, `90e81f5`):
  - `backend/perf_cache.py`: cache de processo com TTL + `cache_clear(prefix)`.
  - N+1 eliminado: inscrições (40→3), alunos (24→4), convocar/chamada/oradores/dpos/delegações/documentos (eager `selectinload(Delegation.students)` + `joinedload(inscription/theme)` via `_helpers.delegation_options()`).
  - Dashboard: todos os COUNTs em 1 query (`_cnt()` de módulo), queries mortas removidas (`recent_students`, `pending_inscriptions`, `days_agenda`, `inscricoes_abertas` não eram usados no template), `current_agenda` só quando a fase é `during`.
  - `EventConfig.get_state()`: fase + invoke + inscrições em 1 query/TTL 60s (invalida nos setters).
  - `SystemConfig.get`: 1ª leitura carrega todas as chaves de 1 vez (notificações 10→2 queries).
  - `get_agenda_status()`: min/max compostos em 1 query (eram 2) + TTL 60s.
  - Fix 500 `/admin/diretor` (`UnboundLocalError` de `func` local) e fix `.strftime` em string na agenda (`agenda_list.html`).
- **Resultado em produção** (pass 2): dashboard 3,7 s/20q → **1,29 s/4q**; inscrições 7,4 s/40q → **1,12 s/3q**; notificações 2,7 s/14q → **0,75 s/1q**; páginas comuns 1,26 s/6q → **0,93–1,12 s/2q**; diretor 500 → **1,82 s/6q**.

### Telão (`GET /telao`) + correções de segurança/dados
- **Arquitetura**: SPA pública em `backend/templates/telao.html` + `static/js/telao.js` + `static/css/telao.css`; rota `vote.py::telao`; estado `GET /api/telao/estado`; Socket.IO room `telao` (7 arquivos de rota emitem para ele); polling 15s (WS) / 5s (sem WS).
- **Bugs corrigidos**:
  -- `<div class="t-main">` nunca fechado desde o commit inicial → ticker agora é filho de `body` e gruda na base (flex).
  -- Timer de debate: handlers `debate_timer_*` agora exigem moderator (antes qualquer anônimo controlava); botões ▶/↺ só renderizam para mesa (`can_control` no template).
  -- `POST /api/vote/<id>/auto_close` removido do cliente (sem login/CSRF falhava); auto-close é server-side.
  -- XSS: `esc()` + novo `safeUrl()` (só http(s)/relativo) em `flag`/`flag_url`/títulos do ticker.
  -- Fila de oradores volta após cada fala; resultado volta ao idle em 12s; dedupe de `vote_closed` repetido.
- **Restauração de tela (Fase D)**: `backend/telao_state.py` grava a tela ativa em `SystemConfig` (`telao_state`) nos endpoints `*/telao` show/hide; `/api/telao/estado` devolve `display` com payload reconstruído do banco; `telao.js` reaplica quando o `ts` muda (F5/reboot do projetor volta à tela certa).
- **Admin — perda de dados corrigida**:
  -- `student_delete` não apaga mais votos/inscrição/delegação do grupo inteiro (usa `_cleanup_orphan_delegation` + checagens de referência).
  -- `period_delete` bloqueado se o período tem itens de agenda (senão `period_id` era anulado).
- **Limpeza**: `admin.py.bak` removido; `pypdf`/`reportlab` fora dos requirements; rotas mortas removidas (`agenda_set_status`, `certificate_sign/unsign`, `student_remove_member`); botões criados para `students_unlock_all` (dashboard) e `inscricoes_toggle` (delegações); `gestao_endpoints`/`simulacao_endpoints` removidos do `base.html`; `_sign_certificate` não commita mais por aluno (1 commit por lote).

---

## Active
- Resta o gargalo de **latência por query (~175 ms)**: perguntar ao usuário o host/região do `DATABASE_URL` (linha `DB target:` dos logs do Render). Mover o DB para a mesma região do app deve derrubar páginas para ~300 ms.

## Blocked
- `git push` may time out on some networks; retry with `git push --verbose`

## Key Files
| File | Purpose |
|------|---------|
| `pages/css/variables.css` | Crisis banner CSS (fixed, z-index: 100, body class push) |
| `pages/js/main.js` | Global JS sem lógica de crisis (só navbar, scroll, counter) |
| `pages/noticias.html` | Inline JS: loadCrisisBanner + setInterval 60s |
| `pages/index.html`, `comites.html`, etc. | Cada página com inline script de crisis banner independente |
| `backend/models/delegation.py` | Delegation model (country, theme, presence, DPO) |
| `backend/models/student.py` | Student model (certificate hash, delegation link) |
| `backend/routes/admin/` | Pacote admin: 20 submódulos (dashboard, students, delegations, certificates, agenda, attendance...) |
| `backend/routes/admin/_helpers.py` | Blueprint, decorators, context processor cacheado, `_cleanup_orphan_delegation()` |
| `backend/routes/student.py` | Student dashboard, DPO upload, auto-certificates |
| `backend/routes/vote.py` | Certificate view, voting, rota `/telao` + `/api/telao/estado` |
| `backend/templates/telao.html` | Telão SPA (8 telas + ticker) |
| `backend/static/js/telao.js` | Telão: WS room `telao`, polling, restauração de tela |
| `backend/telao_state.py` | Estado da tela ativa do telão (SystemConfig `telao_state`) |
| `backend/routes/api.py` | API pública (noticias, ticker, `noticia-json/<slug>`, status) |
| `backend/app.py` | Instrumentação de perf (headers, SLOW, `DB target:`) |
| `backend/perf_probe.py` | Sonda HTTP de produção (TTFB/srv/db/queries) |
| `backend/test_perf_pages.py` | Harness local de smoke/perf (18 rotas) |
| `backend/perf_cache.py` | Cache de processo com TTL/invalidação |
| `backend/templates/admin/delegation_create.html` | New delegation form |
| `backend/templates/admin/dpos_list.html` | DPO list with delete button |
| `backend/static/css/student.css` | External CSS for student panel |
| `swdl-web/components/noticias/*` | Portal (CategoryBar, LeadStory, TopStories, etc.) |
| `swdl-web/app/[locale]/noticia/[slug]/page.tsx` | Página de artigo Next.js |
| `swdl-web/lib/api.ts` | Cliente API (`noticia` → `/noticia-json`) |
