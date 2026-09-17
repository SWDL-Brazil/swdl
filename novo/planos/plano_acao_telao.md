# Plano de Ação — Telão SWDL

> Última atualização: 13/09/2026
> 20 itens | Esforço estimado: ~12h

---

## Legenda

- **Status**: `pendente` | `em_andamento` | `concluido`
- **Prioridade**: `critica` | `alta` | `media` | `baixa`
- **Estimativa**: tempo por item em minutos

---

## FASE 1 — Bugs Críticos

> Funcionalidades quebradas no telão ao vivo — impacto direto no evento.

| # | Status | Prioridade | Issue | Arquivo:linha | Correção | Est. |
|---|--------|-----------|-------|---------------|----------|------|
| 1.1 | concluido | critica | `chamada_update` emitido mas sem listener — presença individual perdida | `admin/attendance.py:45` + `telao.js:646-679` | Adicionar `socket.on('chamada_update', ...)` que move delegação entre colunas | 30min |
| 1.2 | concluido | critica | `Motion.pending_for_committee(None)` filtra `committee IS NULL` — "Todos" quebrado | `models/motion.py:73-76` + `motion.py:228` | Quando None, não aplicar filtro de committee | 15min |
| 1.3 | concluido | critica | `Resolution.query.filter_by(committee=None)` — mesmo bug "Todos" | `resolution.py:37-47` + `resolution.py:188` | Quando None, usar query sem filtro | 15min |

**Subtotal: ~60min**

---

## FASE 2 — Bugs Médios/Altos

> Issues que afetam a experiência mas não quebram completamente.

| # | Status | Prioridade | Issue | Arquivo:linha | Correção | Est. |
|---|--------|-----------|-------|---------------|----------|------|
| 2.1 | pendente | alta | Timer de debate 100% local — reseta ao recarregar | `telao.js:47-82` | Criar Socket.IO events `debate_timer_*` + persistir em EventConfig | 60min |
| 2.2 | concluido | alta | Race condition auto-close votação (client + server) | `telao.js:696-699` + `vote.py:340-348` | Remover auto-close client-side, só server controla | 15min |
| 2.3 | concluido | media | `oradoresScreen` no SCREENS mas não existe `<div>` | `telao.js:12` | Remover do array (usa overlay dinâmico) | 2min |
| 2.4 | pendente | media | Resultado auto-volta idle após 12s sem controle admin | `telao.js:307` | Tornar configurável ou remover auto-hide | 10min |
| 2.5 | pendente | media | Multi-comitê ignorado: `join_telao` envia 1ª sessão | `vote.py:264-266` | Enviar todas as sessões abertas | 15min |
| 2.6 | concluido | media | XSS: `innerHTML` sem sanitização em 8+ lugares | `telao.js:249,325,333,342,373,418,461-466` | Criar função `esc()` e usar em todos os pontos | 20min |
| 2.7 | concluido | baixa | `print()` em produção | `admin/speakers.py:80` | Trocar por `logger.debug()` | 2min |

**Subtotal: ~124min**

---

## FASE 3 — Qualidade de Código

> Melhorias de manutenibilidade e robustez.

| # | Status | Prioridade | Issue | Arquivo | Correção | Est. |
|---|--------|-----------|-------|---------|----------|------|
| 3.1 | concluido | media | CSS variables duplicadas | `telao.css:5-13` + `variables.css` | Remover `:root` de `telao.css` | 5min |
| 3.2 | concluido | media | Polling sempre 5s (comentário "adaptive" mentiroso) | `telao.js:722` | Intervalo adaptivo: 5s com WS, 2s sem | 10min |
| 3.3 | concluido | media | `speech_timer_reset` muda para idle mesmo com fila visível | `telao.js:670` | Verificar se `speakerQueueScreen` ativo antes de mudar | 10min |
| 3.4 | concluido | baixa | `oradores_toggle` usa CSS selector frágil | `telao.js:660,709` | Adicionar `id` ao elemento, usar `$id()` | 10min |
| 3.5 | concluido | baixa | Sem indicador de desconexão WebSocket | `telao.js:654` | Badge discreto no header | 10min |
| 3.6 | pendente | baixa | Template monolítico (281+724+435 linhas) | `telao.html/js/css` | Considerar extrair JS para módulos | 60min |

**Subtotal: ~105min**

---

## FASE 4 — Features Ausentes

> Funcionalidades novas para melhorar o telão.

| # | Status | Prioridade | Feature | Descrição | Est. |
|---|--------|-----------|---------|-----------|------|
| 4.1 | pendente | alta | Controle remoto do timer de debate | Rotas admin `POST /admin/debate-timer/*` + Socket.IO | 60min |
| 4.2 | pendente | media | Indicador de status da conexão | Badge "🔴 Desconectado" / "🟢 Conectado" | 15min |
| 4.3 | pendente | media | Duração do resultado configurável | Input admin para definir segundos (default 12s) | 20min |
| 4.4 | pendente | baixa | Suporte a multi-comitê | Tabs ou telas separadas por comitê | 90min |

**Subtotal: ~185min**

---

## Resumo

| Fase | Itens | Esforço |
|------|-------|---------|
| Fase 1 — Bugs Críticos | 3 | ~60min |
| Fase 2 — Bugs Médios/Altos | 7 | ~124min |
| Fase 3 — Qualidade de Código | 6 | ~105min |
| Fase 4 — Features Ausentes | 4 | ~185min |
| **Total** | **20** | **~8h** |

---

## Arquivos Envolvidos

### Rotas (emissões para telão)
`vote.py`, `admin/attendance.py`, `admin/speakers.py`, `admin/timer.py`, `speaker_queue.py`, `motion.py`, `resolution.py`

### Template
`telao.html` (SPA monolítica com 9 telas)

### Models
`speaker.py`, `motion.py`, `resolution.py`

### CSS/JS
`telao.js` (724 linhas), `telao.css` (435 linhas), `variables.css`
