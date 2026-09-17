# Plano de Ação — Painel Admin SWDL

> Última atualização: 13/09/2026
> 24 itens | Esforço estimado: ~13-14h

---

## Legenda

- **Status**: `pendente` | `em_andamento` | `concluido`
- **Prioridade**: `critica` | `alta` | `media` | `baixa`
- **Estimativa**: tempo por item em minutos

---

## FASE 1 — Bugs Críticos

> Causam erros em runtime. Corrigir antes de qualquer outra coisa.

| # | Status | Prioridade | Issue | Arquivo:linha | Correção | Est. |
|---|--------|-----------|-------|---------------|----------|------|
| 1.1 | concluido | critica | `abort(400)` sem import → NameError | `admin/agenda.py:1` | Adicionar `abort` ao import de flask | 5min |
| 1.2 | concluido | critica | `bare except` engole erros | `admin/certificates.py:120-121` | Trocar `except:` por `except OSError:` | 5min |
| 1.3 | pendente | critica | `os.path.isfile()` recebe URL completa | `admin/certificates.py:101` + `vote.py:282` | Salvar path local em `certificate_url` | 15min |
| 1.4 | concluido | alta | Import duplicado `sqlalchemy.func` | `admin/dashboard.py:45,57` | Remover `f2`, usar `func` existente | 5min |
| 1.5 | concluido | alta | Import não usado `jsonify` | `admin/agenda.py:1` | Remover `jsonify` do import | 2min |

**Subtotal: ~32min**

---

## FASE 2 — Funcionalidade Quebrada

> Funcionalidades que não funcionam como esperado.

| # | Status | Prioridade | Issue | Arquivo | Correção | Est. |
|---|--------|-----------|-------|---------|----------|------|
| 2.1 | concluido | alta | Crisis é stub — apenas flash, não persiste | `admin/crisis.py` | Criar campo `crisis_active` + `crisis_message` no EventConfig. Emitir WebSocket. Integrar com agenda | 60min |
| 2.2 | concluido | media | Inscrição aprovação cria Delegation órfã | `admin/inscriptions.py:73-78` | Não criar Delegation na aprovação | 15min |

**Subtotal: ~75min**

---

## FASE 3 — Segurança

> Issues que comprometem a segurança da aplicação.

| # | Status | Prioridade | Issue | Arquivo | Correção | Est. |
|---|--------|-----------|-------|---------|----------|------|
| 3.1 | pendente | alta | Senhas fracas (`first4+year`) | `students.py:35`, `delegations.py:111,240`, `inscriptions.py:57` | Usar `secrets.token_urlsafe(8)` | 20min |
| 3.2 | pendente | alta | Delete cascade sem confirmação | `admin/delegations.py:172-214` | Checkbox confirmação + 2ª tela | 30min |
| 3.3 | concluido | media | Credenciais SMTP hardcoded | `admin/notifications.py:60` | Usar variável de config | 5min |
| 3.4 | concluido | media | CSS inline ~375 linhas | `admin/base.html:11-375` | Extrair para `admin/static/admin.css` | 30min |
| 3.5 | pendente | media | `moderator_required` duplicado em 5 arquivos | `_helpers.py`, `vote.py`, `speaker_queue.py`, `motion.py`, `resolution.py` | Consolidar em `_helpers.py` | 20min |

**Subtotal: ~105min**

---

## FASE 4 — Qualidade de Código

> Melhorias de manutenibilidade e robustez.

| # | Status | Prioridade | Issue | Arquivo | Correção | Est. |
|---|--------|-----------|-------|---------|----------|------|
| 4.1 | pendente | media | Imagens órfãs ao substituir tema/noticia | `themes.py:69`, `news.py:77` | Deletar arquivo antigo antes de salvar novo | 15min |
| 4.2 | concluido | media | `EventConfig._ensure()` faz commit em leitura | `models/event_config.py` | Usar `flush()` em vez de `commit()` | 10min |
| 4.3 | concluido | baixa | Context processor engole exceções | `admin/_helpers.py:56-58` | Adicionar `logger.error()` antes do fallback | 5min |
| 4.4 | concluido | baixa | `print()` em produção | `admin/speakers.py:80` | Trocar por `current_app.logger.debug()` | 2min |
| 4.5 | pendente | baixa | Migrações SQL raw frágeis | `app.py:105-220` | Documentar ou migrar para Alembic | 30min |

**Subtotal: ~62min**

---

## FASE 5 — Features Ausentes

> Funcionalidades novas que melhoram a experiência do admin.

| # | Status | Prioridade | Feature | Descrição | Est. |
|---|--------|-----------|---------|-----------|------|
| 5.1 | pendente | alta | Editar aluno | Rota `GET/POST /alunos/<id>/editar` + template | 45min |
| 5.2 | pendente | alta | Busca/paginação | Busca por nome/email + paginação em listas | 60min |
| 5.3 | pendente | alta | Confirmação delete delegação | Checkbox "Entendo que deletará X alunos" | 20min |
| 5.4 | pendente | media | Deletar aluno | Rota `POST /alunos/<id>/deletar` com confirmação | 20min |
| 5.5 | pendente | media | Gerenciamento de Users | Rota `/admin/usuarios` listar/editar/deletar | 60min |
| 5.6 | pendente | media | Audit log completo | Expandir `AuditLog` para todas ações admin | 45min |
| 5.7 | pendente | baixa | Toggle tema/noticia publicado | Toggle rápido inline na lista | 15min |

**Subtotal: ~265min**

---

## Resumo

| Fase | Itens | Esforço |
|------|-------|---------|
| Fase 1 — Bugs Críticos | 5 | ~32min |
| Fase 2 — Funcionalidade Quebrada | 2 | ~75min |
| Fase 3 — Segurança | 5 | ~105min |
| Fase 4 — Qualidade de Código | 5 | ~62min |
| Fase 5 — Features Ausentes | 7 | ~265min |
| **Total** | **24** | **~8-9h** |

---

## Arquivos Envolvidos

### Rotas Admin (21)
`__init__.py`, `_helpers.py`, `dashboard.py`, `students.py`, `delegations.py`, `inscriptions.py`, `news.py`, `categories.py`, `themes.py`, `agenda.py`, `documents.py`, `alerts.py`, `dpos.py`, `convocation.py`, `certificates.py`, `attendance.py`, `speakers.py`, `timer.py`, `crisis.py`, `invocation.py`, `notifications.py`

### Blueprints Externos (5)
`vote.py`, `speaker_queue.py`, `motion.py`, `resolution.py`, `analytics.py`

### Templates (37)
`base.html`, `login.html`, `dashboard.html`, `dashboard_director.html`, `students_list.html`, `delegate_create.html`, `student_assign.html`, `delegations_list.html`, `delegation_create.html`, `delegation_assign.html`, `inscriptions_list.html`, `inscription_detail.html`, `news_list.html`, `news_form.html`, `categories_list.html`, `themes_list.html`, `agenda_list.html`, `agenda_form.html`, `documentos_list.html`, `alerts_list.html`, `dpos_list.html`, `convocar.html`, `certificates_list.html`, `chamada.html`, `oradores.html`, `cronometro.html`, `speaker_queue.html`, `motions.html`, `motion_form.html`, `resolutions.html`, `resolution_view.html`, `vote_list.html`, `vote_form.html`, `vote_results.html`, `invocar.html`, `notifications_config.html`, `analytics.html`
