# SWDL — Session Summary

## Objective
Build a complete student panel + admin backend for the SWDL Model UN platform with agenda-based auto-locking, PDF certificate template rendering, and no manual phase switching.

---

## Completed

### Student Panel
- "Meu Debate" highlight card on dashboard when delegation assigned
- DPO deadline check (3 days before 1st agenda item)
- Voting auto-unlock on event day (`is_event_day` flag)
- Auto-compile certificates with PDF rendering when event ends
- Student certificates page listing released certificates

### Admin Panel
- **DPO Management**: List, download, delete DPOs (resets so student can re-upload)
- **Delegation Create Form**: Theme + Country + Student selection (1 to 4+ students)
  -- Creates Inscription, User (login), ParticipationHistory automatically
- **Certificate Templates (PDF)**:
  -- Admin uploads PDF (blank certificate design)
  -- Admin positions fields via X/Y coordinates (points, bottom-left origin)
  -- 10 placeholders: student_name, country, country_flag, committee, theme, edition_year, date, global_id, certificate_hash, digital_signature
  -- Uses pypdf + reportlab to overlay text on PDF
  -- Preview generates live PDF with student data
  -- Auto-compile at event end renders per-student PDFs
  -- `certificate_view` serves the generated PDF file

### Infrastructure
- `datetime.utcnow` replaced with `datetime.now(timezone.utc)` everywhere
- Hardcoded email and year removed from templates
- CSS extracted to external file `student.css`
- Manual phase system removed → `get_agenda_status()` driven by agenda items
- Added database indexes on all frequently queried columns
- Removed `available_themes` from context_processor (was running on every page)
- Consolidated dashboard COUNT queries (20→3)
- Added `pypdf` and `reportlab` to requirements

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
| `backend/models/certificate_template.py` | PDF template model with render_pdf() |
| `backend/models/delegation.py` | Delegation model (country, theme, presence, DPO) |
| `backend/models/student.py` | Student model (certificate hash, delegation link) |
| `backend/routes/admin.py` | All admin routes (CRUD templates, delegations, DPO, dashboard) |
| `backend/routes/student.py` | Student dashboard, DPO upload, auto-certificates |
| `backend/routes/vote.py` | Certificate view endpoint, voting |
| `backend/routes/api.py` | API pública (noticias, ticker, `noticia-json/<slug>`, status) |
| `backend/app.py` | Instrumentação de perf (headers, SLOW, `DB target:`) |
| `backend/perf_probe.py` | Sonda HTTP de produção (TTFB/srv/db/queries) |
| `backend/test_perf_pages.py` | Harness local de smoke/perf (18 rotas) |
| `backend/perf_cache.py` | Cache de processo com TTL/invalidação |
| `backend/routes/admin/_helpers.py` | Context processor cacheado + `delegation_options()` |
| `backend/templates/admin/certificate_templates.html` | Template list |
| `backend/templates/admin/certificate_template_form.html` | Template form with PDF upload + field positioning |
| `backend/templates/admin/delegation_create.html` | New delegation form |
| `backend/templates/admin/dpos_list.html` | DPO list with delete button |
| `backend/static/css/student.css` | External CSS for student panel |
| `swdl-web/components/noticias/*` | Portal (CategoryBar, LeadStory, TopStories, etc.) |
| `swdl-web/app/[locale]/noticia/[slug]/page.tsx` | Página de artigo Next.js |
| `swdl-web/lib/api.ts` | Cliente API (`noticia` → `/noticia-json`) |
