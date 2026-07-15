# SWDL V.2 — Relatório de Implementação

**Projeto:** SESI CE-437 — Pedro dos Santos Bonazzi Pereira (N°28, 1°B)  
**Plataforma:** SWDL — Sesi World Diplomacy League  
**Ano:** 2026

---

## Capítulo 1 — Diretrizes do Sistema (RBAC)

### 1.2 Mapeamento de Papéis

| Papel | Acesso | Implementação |
|---|---|---|
| **Administrador** | Full access | `is_admin()` — True apenas para role `admin` |
| **Mesa Diretora** | Moderação (presença, votações, oradores) sem acesso à Gestão | `is_director()` + `is_moderator()` — decorators `admin_required` (admin only) e `moderator_required` (admin+director) |
| **Aluno** | Própria delegação, presença, votação, certificados | Role `student` com rotas protegidas por `@student_required` |

**Arquivos:** `models/user.py`, `routes/admin.py`, `templates/admin/base.html`

---

## Capítulo 2 — Arquitetura de Redes e Fluxo de Dados

### 2.1 Inscrição e Geração de Credenciais

- **Formulário público:** `POST /api/inscricao` — coleta name, email, phone, school, grade, partner_name, motivation, interests
- **Revisão admin:** `GET /admin/inscricoes` — lista com filtro por status; detalhe com motivação
- **Auto-criação de contas:** Ao aprovar, o sistema cria automaticamente:
  - `User` (role=student, senha padrão `{primeiras4letras}2025`)
  - `Student` (com ID Global único UUID4)
  - `Delegation` (vinculada ao User + Inscription)
- **Credenciais exibidas:** No flash message e na página de detalhe da inscrição
- **Campo `school`:** Adicionado ao model `Inscription` conforme especificação

**Arquivos:** `models/inscription.py`, `routes/admin.py` (`inscription_approve`), `routes/api.py` (`api_inscricao`), `templates/admin/inscription_detail.html`

### 2.2 Hub de Distribuição de Notícias

- CRUD completo de notícias no admin (criar, editar, deletar, publicar/rascunho)
- Lista pública via API (`GET /api/noticias`)
- Página do aluno em `/student/comunicados`
- Suporte a categorias, imagem de capa, crise banner

**Arquivos:** `models/news.py`, `routes/admin.py`, `routes/api.py`, `routes/student.py`, `templates/admin/news_form.html`, `templates/student/comunicados.html`

### 2.3 Topologia de Conectividade do Telão

- Página pública `/telao` (sem login)
- WebSocket em tempo real: votações (abrir/fechar/atualizar), ticker de notícias, fila de oradores
- API de estado: `GET /api/telao/estado` — retorna sessão, ticker, oradores
- Isolamento de streams: apenas dados de votação trafegam no room `telao`

**Arquivos:** `routes/vote.py`, `templates/telao.html`

---

## Capítulo 3 — Módulos Core e Engenharia de Interface

### 3.1 Identidade Unificada, Histórico Global e Invocação

- **ID Global:** `Student.global_id` — UUID4 único e permanente por aluno
- **Histórico Global:** `ParticipationHistory` — registra ano, país, comitê, tema, papel por edição
- **Criação automática de histórico:** `_ensure_participation_history()` ao convocar aluno
- **Invocação individual:** `POST /admin/convocar/<id>/toggle`
- **Invocação em lote:**
  - `POST /admin/convocar/todos` — convoca todos pendentes
  - `POST /admin/convocar/desconvocar-todos` — limpa geral
  - `POST /admin/convocar/por-tema/<theme_id>` — convoca por tema/debate
- Interface com botões de lote e estatísticas (total/convocados/pendentes)

**Arquivos:** `models/student.py`, `models/participation.py`, `routes/admin.py`, `templates/admin/convocar.html`

### 3.2 Dashboard Adaptativo (Upgrade 5)

- **3 fases:** `pre`, `during`, `post` — cada uma com layout, checklist e métricas específicas
- **Admin:** cards, app-launcher e checklist adaptados por fase
- **Diretor:** dashboard próprio em `/admin/diretor` com visão de moderação
- **App-switcher:** o app padrão muda conforme a fase (gestão → simulação → certificados)
- Sidebar condicional: Gestão oculta para diretores

**Arquivos:** `routes/admin.py`, `templates/admin/dashboard.html`, `templates/admin/dashboard_director.html`, `templates/admin/base.html`

### 3.3 Documentos e Consolidação de Streams

- Model `Document` com categoria (`guias`, `comunicados`, `resolucoes`, `mesa`)
- Admin faz upload com categoria e vínculo opcional a tema
- **Filtro por categoria no aluno:** Abas "Todas", "Guias", "Comunicados", "Resoluções", "Mesa" em `/student/documentos`
- Filtro combinado: categoria + documentos do tema do aluno

**Arquivos:** `models/document.py`, `routes/student.py`, `templates/student/documentos.html`

### 3.4 Flexibilidade de Composição de Delegações

- Designação de país, tema, dupla (parceiro)
- **Toggle `flag_animation`:** Checkbox "Animação da bandeira no telão" nos formulários de designação
- Preservação da integridade lógica em reassignações

**Arquivos:** `routes/admin.py`, `templates/admin/delegation_assign.html`, `templates/admin/student_assign.html`

---

## Capítulo 4 — Recursos Experimentais

### 4.1 Chamada Adaptativa (🧪 Experimental)

- **Triagem de dispositivo:** Detecção de mobile/touch/offline na página de presença
- **Quick-mode:** Registro de presença + logout automático para dispositivos compartilhados
- **Integridade:** Votação bloqueada via API (403) se `presence_status == 'ausente'`
- **adapted_device:** flag para alunos que usaram dispositivo adaptado

**Arquivos:** `routes/student.py`, `templates/student/attendance.html`, `templates/student/voting.html`

### 4.2 Certificação Automática (🧪 Experimental)

- **Algoritmo de compilação:** Varre alunos com presença (`presente`/`votante`) e gera UUID + URL pública
- **Gestão admin:** `/admin/certificados` — tabela com status, hash, liberação; ações individuais e em lote
- **Gatilho automático:** Ao mudar fase para `post`, compila certificados automaticamente
- **Visualização pública:** `/certificado/<hash>` — página estilizada com nome, delegação, selo de validade
- **API de validação:** `GET /api/certificado/validar?hash=xxx`

**Arquivos:** `routes/admin.py`, `routes/vote.py`, `routes/student.py`, `templates/admin/certificates_list.html`, `templates/public/certificate_view.html`

### 4.3 Assinaturas Digitais + DPO + Auditoria

#### Assinaturas HMAC-SHA256
- `Student.compute_signature(secret)` — gera HMAC com dados do aluno + secret key
- `Student.verify_signature(secret)` — verificação usando `hmac.compare_digest`
- Admin pode assinar individualmente ou em lote
- Selo "🖊️ Assinado Digitalmente" na página pública e do aluno
- API de validação retorna `digital_signature` e `signature_valid`

#### Upload de DPO pelo Aluno
- `POST /student/dpo/enviar` — aceita PDF, salva em `static/uploads/dpo/`
- Atualiza `delegation.dpo_path` e `delegation.dpo_uploaded`
- Seção no perfil do aluno com status e formulário de upload
- Admin pode baixar DPOs em `/admin/dpos`

#### Audit Trail
- Model `AuditLog` registra: ação, alvo, usuário, data, detalhes
- Logging em toda ação de certificado: compilar, assinar, liberar, reverter
- Painel de auditoria visível na página de certificados admin

**Arquivos:** `models/student.py`, `models/audit_log.py`, `models/delegation.py`, `routes/admin.py`, `routes/student.py`, `templates/student/profile.html`, `templates/public/certificate_view.html`, `templates/admin/certificates_list.html`

### 4.4 Validação Externa de Autenticidade

- Hash criptográfico UUID4 por certificado
- Endpoint público: `GET /api/certificado/validar?hash=xxx`
- Retorna: nome, URL, status da assinatura digital, data
- Página pública de certificado inválido (404 amigável)

**Arquivos:** `routes/student.py`, `templates/public/certificate_invalid.html`

---

## Capítulo 5 — Segurança e Integridade Pós-Evento

### 5.1 Travamento Pós-Simulação

- **Automático:** Ao mudar fase para `post`, todos os alunos recebem `read_only = True`
- **Automático (volta):** Ao voltar para `pre`/`during`, todos são destravados
- **Manual:** Botões 🔒 Travar / 🔓 Destravar no dashboard admin
- **Indicador:** Badge `🔒 X/Y travados` ao lado dos botões de fase
- **Proteção nas rotas:** `check_read_only()` redireciona aluno com flash em presença, votação e API
- **Checklist pós-sessão:** Item "Alunos travados (X/Y)" com botão contextual

**Arquivos:** `routes/admin.py`, `routes/student.py`, `templates/admin/dashboard.html`

---

## Implantação

```bash
cd backend
python app.py
```

- Admin: `/admin/login`
- Aluno: `/student/login`
- Telão: `/telao`

---

*Documento gerado automaticamente em 14/07/2026.*
