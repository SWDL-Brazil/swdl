# Plano de Ação — Painel do Estudante SWDL

> Última atualização: 13/09/2026
> 22 itens | Esforço estimado: ~11h

---

## Legenda

- **Status**: `pendente` | `em_andamento` | `concluido`
- **Prioridade**: `critica` | `alta` | `media` | `baixa`
- **Estimativa**: tempo por item em minutos

---

## FASE 1 — Bugs Críticos

> Funcionalidades completamente quebradas.

| # | Status | Prioridade | Issue | Arquivo:linha | Correção | Est. |
|---|--------|-----------|-------|---------------|----------|------|
| 1.1 | concluido | critica | `getattr(current_user, 'student')` sempre retorna None — relationship se chama `student_profile` | `motion.py:252`, `resolution.py:203` | Trocar `'student'` por `'student_profile'` | 5min |
| 1.2 | concluido | critica | Template usa `n.category` mas model só tem `category_id` (FK) | `student/comunicados.html:19,22` | Trocar por `n.category_obj.name if n.category_obj else 'geral'` | 10min |
| 1.3 | concluido | alta | Nav some em mobile (`display:none` @768px) sem hamburger | `student.css:594` | Adicionar hamburger no `base.html` + CSS | 30min |
| 1.4 | concluido | alta | `certificate_url` salva URL completa mas `os.path.isfile()` espera path | `admin/certificates.py:101` + `vote.py:282` | Salvar path local (mesmo fix do admin 1.3) | 15min |
| 1.5 | concluido | alta | Rotas `/delegado/*` não estão na nav — features huérfanas | `student/base.html` | Adicionar links (após fix 2.1) | 10min |

**Subtotal: ~70min**

---

## FASE 2 — Funcionalidades Quebradas

> Rotas que existem mas não funcionam corretamente.

| # | Status | Prioridade | Issue | Arquivo | Correção | Est. |
|---|--------|-----------|-------|---------|----------|------|
| 2.1 | concluido | alta | Moções e resoluções não acessíveis da nav | `student/base.html`, `motion.py`, `resolution.py` | Adicionar endpoints na nav + importar `moderator_required` de `_helpers.py` | 20min |
| 2.2 | pendente | alta | `Delegation.query.filter_by(user_id=...)` inconsistente com `get_student()` | `vote.py`, `motion.py:256,280,338`, `resolution.py:207,226,265,291,315,335` | Unificar para usar helper `get_student()` + `get_delegation()` | 30min |
| 2.3 | pendente | media | `read_only` não verificado em moções/resoluções | `motion.py:276,329`, `resolution.py:221,259,285,309,329` | Adicionar `check_read_only()` no início de cada mutation | 15min |

**Subtotal: ~65min**

---

## FASE 3 — Qualidade de Código

> Melhorias de performance e manutenibilidade.

| # | Status | Prioridade | Issue | Arquivo | Correção | Est. |
|---|--------|-----------|-------|---------|----------|------|
| 3.1 | concluido | media | `Delegation.query.get()` deprecated SQLAlchemy 2.0 | `student.py:35` | Usar `db.session.get(Delegation, id)` | 5min |
| 3.2 | concluido | media | Context processor roda 2+ queries por página | `student.py:57` | Cache `is_event_day` em `flask.g` | 10min |
| 3.3 | pendente | baixa | DPO upload sem confirmação de sobrescrita | `student.py:336` | Adicionar `confirm()` JS no form | 5min |
| 3.4 | pendente | baixa | Socket.IO sem fallback visual | `dashboard.html:321-338` | Adicionar `sio.on('connect_error', ...)` | 10min |
| 3.5 | concluido | baixa | `print()` em produção | `admin/speakers.py:80` | Trocar por `logger.debug()` | 2min |

**Subtotal: ~32min**

---

## FASE 4 — Segurança

> Proteção contra abusos e Consistência.

| # | Status | Prioridade | Issue | Arquivo | Correção | Est. |
|---|--------|-----------|-------|---------|----------|------|
| 4.1 | concluido | media | Sem rate limiting em DPO upload | `student.py` | Adicionar check manual ou `flask-limiter` | 15min |
| 4.2 | concluido | media | `moderator_required` duplicado em `motion.py:17` e `resolution.py:18` | `motion.py`, `resolution.py` | Consolidar em `admin/_helpers.py` | 10min |
| 4.3 | concluido | baixa | Document download sem try/except | `student.py:245` | Adicionar `try/except PermissionError` | 5min |

**Subtotal: ~30min**

---

## FASE 5 — Features Ausentes

> Funcionalidades novas para melhorar a experiência do estudante.

| # | Status | Prioridade | Feature | Descrição | Est. |
|---|--------|-----------|---------|-----------|------|
| 5.1 | pendente | alta | Hamburger menu mobile | Botão + JS toggle + CSS animação (similar ao admin) | 45min |
| 5.2 | pendente | alta | Editar perfil / trocar senha | Rota `GET/POST /student/perfil/editar` + template | 45min |
| 5.3 | pendente | media | Notificações persistentes | Model `StudentNotification` + rota + badge | 90min |
| 5.4 | pendente | baixa | Loading states | Spinner no voto e upload DPO | 15min |
| 5.5 | pendente | baixa | Confirmação DPO | `confirm()` antes de sobrescrever | 5min |
| 5.6 | pendente | baixa | Badge moções/resoluções na nav | Contador de pendentes | 15min |

**Subtotal: ~215min**

---

## Resumo

| Fase | Itens | Esforço |
|------|-------|---------|
| Fase 1 — Bugs Críticos | 5 | ~70min |
| Fase 2 — Funcionalidades Quebradas | 3 | ~65min |
| Fase 3 — Qualidade de Código | 5 | ~32min |
| Fase 4 — Segurança | 3 | ~30min |
| Fase 5 — Features Ausentes | 6 | ~215min |
| **Total** | **22** | **~7h** |

---

## Arquivos Envolvidos

### Rotas
`student.py`, `vote.py`, `motion.py`, `resolution.py`, `auth.py`, `admin/certificates.py`, `admin/speakers.py`

### Templates (13)
`base.html`, `login.html`, `dashboard.html`, `attendance.html`, `voting.html`, `documentos.html`, `comunicados.html`, `certificados.html`, `profile.html`, `history.html`, `motions.html`, `resolutions.html`, `_macros.html`

### Models
`student.py`, `user.py`, `news.py`, `category.py`, `delegation.py`

### CSS/JS
`student.css`, `student-attendance.js`, `student-voting.js`

### Blueprints Externos
`vote_bp`, `motion_bp`, `resolution_bp`
