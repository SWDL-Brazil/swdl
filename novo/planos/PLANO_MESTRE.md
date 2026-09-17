# Plano de Ação Mestre — SWDL

> Última atualização: 13/09/2026
> 66 itens totais | ~26h de esforço estimado

---

## Visão Geral

| Plano | Arquivo | Itens | Esforço |
|-------|---------|-------|---------|
| [Painel Admin](plano_acao_admin.md) | `plano_acao_admin.md` | 24 | ~8-9h |
| [Painel Estudante](plano_acao_estudante.md) | `plano_acao_estudante.md` | 22 | ~7h |
| [Telão](plano_acao_telao.md) | `plano_acao_telao.md` | 20 | ~8h |
| **Total** | | **66** | **~23-24h** |

---

## Ordem de Execução Recomendada

### Semana 1 — Corrigir o que está quebrado (crítico)

| Prioridade | Itens | Planos | Esforço |
|-----------|-------|--------|---------|
| **Bugs críticos** | admin 1.1-1.5, estudante 1.1-1.5, telão 1.1-1.3 | Todos | ~3h |
| **Funcionalidade quebrada** | admin 2.1-2.2, estudante 2.1-2.3 | Admin + Estudante | ~2h |

**Total Semana 1: ~5h** — Deixa a aplicação funcional e estável.

### Semana 2 — Segurança e qualidade

| Prioridade | Itens | Planos | Esforço |
|-----------|-------|--------|---------|
| **Segurança** | admin 3.1-3.5, estudante 4.1-4.3 | Admin + Estudante | ~2h |
| **Qualidade** | admin 4.1-4.5, estudante 3.1-3.5, telão 3.1-3.6 | Todos | ~3h |

**Total Semana 2: ~5h** — Deixa o código limpo e seguro.

### Semana 3-4 — Features novas

| Prioridade | Itens | Planos | Esforço |
|-----------|-------|--------|---------|
| **Features admin** | admin 5.1-5.7 | Admin | ~4.5h |
| **Features estudante** | estudante 5.1-5.6 | Estudante | ~3.5h |
| **Features telão** | telão 2.1-2.7, 4.1-4.4 | Telão | ~5h |

**Total Semana 3-4: ~13h** — Funcionalidades novas.

---

## Itens Cruzados (afetam múltiplos planos)

| Issue | Planos Afetados | Ação |
|-------|----------------|------|
| `certificate_url` com URL em vez de path | Admin 1.3 + Estudante 1.4 | Corrigir uma vez, resolve ambos |
| `moderator_required` duplicado | Admin 3.5 + Estudante 4.2 | Consolidar em `_helpers.py` |
| `print()` em produção | Admin 4.4 + Estudante 3.5 + Telão 2.7 | Corrigir uma vez em `speakers.py` |

---

## Checklist de Execução

### FASE 1 — Bugs Críticos
- [x] Admin 1.1: `abort` import
- [x] Admin 1.2: `bare except`
- [x] Admin 1.3: `certificate_url` path
- [x] Admin 1.4: import duplicado
- [x] Admin 1.5: import não usado
- [x] Estudante 1.1: `student_profile`
- [x] Estudante 1.2: `n.category`
- [x] Estudante 1.3: hamburger mobile
- [x] Estudante 1.4: certificate path (com admin 1.3)
- [x] Estudante 1.5: nav huérfana
- [x] Telão 1.1: `chamada_update` listener
- [x] Telão 1.2: motion "Todos"
- [x] Telão 1.3: resolution "Todos"

### FASE 2 — Funcionalidade Quebrada
- [x] Admin 2.1: crisis stub
- [x] Admin 2.2: delegation órfã
- [x] Estudante 2.1: nav moções/resoluções
- [x] Estudante 2.2: helper inconsistente
- [x] Estudante 2.3: read_only check
- [x] Telão 2.1: timer debate sync
- [x] Telão 2.2: race condition
- [x] Telão 2.3: oradoresScreen ghost
- [x] Telão 2.4: resultado auto-hide
- [x] Telão 2.5: multi-comitê
- [x] Telão 2.6: XSS
- [x] Telão 2.7: print

### FASE 3 — Segurança
- [x] Admin 3.1: senhas fracas
- [x] Admin 3.2: delete cascade (confirm dialog exists)
- [x] Admin 3.3: SMTP hardcoded
- [x] Admin 3.4: CSS inline → external file
- [x] Admin 3.5: moderator_required (com estudante 4.2)
- [x] Estudante 4.1: rate limiting
- [x] Estudante 4.3: document download

### FASE 4 — Qualidade de Código
- [ ] Admin 4.1: imagens órfãs (needs cleanup script)
- [x] Admin 4.2: EventConfig commit
- [x] Admin 4.3: context processor
- [x] Admin 4.4: print (com estudante 3.5 + telão 2.7)
- [ ] Admin 4.5: migrações (needs manual review)
- [x] Estudante 3.1: deprecated get()
- [x] Estudante 3.2: context processor cache
- [x] Estudante 3.3: DPO confirmação
- [ ] Estudante 3.4: Socket.IO fallback
- [x] Telão 3.1: CSS variables
- [x] Telão 3.2: polling adaptivo
- [x] Telão 3.3: timer reset
- [x] Telão 3.4: CSS selector frágil
- [x] Telão 3.5: indicador conexão
- [ ] Telão 3.6: template monolítico

### FASE 5 — Features Ausentes
- [ ] Admin 5.1: editar aluno
- [ ] Admin 5.2: busca/paginação
- [ ] Admin 5.3: confirmação delete
- [ ] Admin 5.4: deletar aluno
- [ ] Admin 5.5: gerenciamento users
- [ ] Admin 5.6: audit log
- [ ] Admin 5.7: toggle publicado
- [ ] Estudante 5.1: hamburger mobile
- [ ] Estudante 5.2: editar perfil
- [ ] Estudante 5.3: notificações
- [ ] Estudante 5.4: loading states
- [ ] Estudante 5.5: confirmação DPO
- [ ] Estudante 5.6: badge nav
- [ ] Telão 4.1: timer debate admin
- [ ] Telão 4.2: indicador conexão
- [ ] Telão 4.3: resultado configurável
- [ ] Telão 4.4: multi-comitê
