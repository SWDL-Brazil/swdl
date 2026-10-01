# Plano: Atualização do Sistema de Cadastro — Trio/Dupla/Individual

**Data:** 2026-09-17
**Status:** Aguardando aprovação

---

## Objetivo

Permitir inscrições em **trio**, **dupla** ou **individual** em um único formulário dinâmico, coletando dados completos de cada membro, e facilitar a montagem das delegações no painel admin com criação automática de contas na confirmação.

---

## Contexto

O formulário atual (`pages/faca-parte.html`) suporta apenas inscrição individual. O próximo debate será em trio, então precisamos:

1. Formulário dinâmico que adapta os campos conforme formato (individual/dupla/trio)
2. Coletar dados completos de cada membro: nome, email, turma, Instagram, telefone
3. Uma pessoa pode inscrever o grupo todo de uma vez
4. Admin revisa e confirma → criação automática de contas para todos os membros
5. Nem todos que se inscrevem vão participar — equipe organizadora confirma

---

## Fluxo Atual (Problemas)

```
Formulário → POST /api/inscricao → Inscription (status=pending)
                                          ↓
Admin aprova → cria User + Student (APENAS para o inscrito principal)
                                          ↓
Delegação criada separadamente pelo admin
```

**Problemas:**
- Sem suporte a múltiplos membros na inscrição
- Campos `school`, `partner_name` existem no model mas nunca são coletados
- Campo `experience` no form mas não é enviado no payload
- Campo `motivation` no form de voluntário não existe (fd.get('motivation') retorna vazio)
- Sem verificação de email duplicado
- Sem verificação server-side se inscrições estão abertas
- Formulário de voluntário tem campos ignorados no payload JS

---

## Fluxo Desejado

```
1. Estudante preenche form → escolhe Trio/Dupla/Individual
2. Preenche seus dados + dados dos colegas (se aplicável)
3. POST /api/inscricao → cria Inscription + InscriptionMembers
4. Admin vê na lista: "João + 2 membros (Trio)" com status Pendente
5. Admin clica "Ver detalhes" → vê dados de todos os membros
6. Admin clica "Aprovar Inscrição"
7. Sistema:
   a. Verifica se cada membro já tem conta → reusar ou criar
   b. Cria Delegation vinculando todos os students
   c. Gera ParticipationHistory para cada um
   d. Envia credenciais (email/WhatsApp) para cada membro
   e. Flash mostra todas as credenciais geradas
8. Cada membro faz login com seu email + sua senha
```

---

## Fase 1 — Backend: Novos Models

### 1.1 Criar `backend/models/inscription_member.py`

```python
class InscriptionMember(db.Model):
    __tablename__ = 'inscription_members'

    id              = db.Column(db.Integer, primary_key=True)
    inscription_id  = db.Column(db.Integer, db.ForeignKey('inscriptions.id', ondelete='CASCADE'), nullable=False, index=True)
    name            = db.Column(db.String(120), nullable=False)
    email           = db.Column(db.String(120), nullable=False)
    grade           = db.Column(db.String(30))
    instagram       = db.Column(db.String(100))
    phone           = db.Column(db.String(30))
    created_at      = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    inscription = db.relationship('Inscription', backref=db.backref('extra_members', cascade='all, delete-orphan'))
```

### 1.2 Atualizar `backend/models/inscription.py`

Adicionar campos:

| Campo | Tipo | Default | Descrição |
|-------|------|---------|-----------|
| `instagram` | String(100) | `''` | Instagram do inscrito principal |
| `formato` | String(20) | `'individual'` | `'individual'`, `'dupla'`, `'trio'` |

Adicionar relationship:

```python
extra_members = db.relationship('InscriptionMember', backref='inscription', cascade='all, delete-orphan')
```

### 1.3 Migration

```bash
flask db migrate -m "add inscription_member table + instagram/formato to inscription"
flask db upgrade
```

---

## Fase 2 — Backend: API de Inscrição

### 2.1 Atualizar `api_inscricao()` em `backend/routes/api.py`

Payload esperado:

```json
{
  "name": "João Silva",
  "email": "joao@portalsesisp.org.br",
  "phone": "(11) 99999-0000",
  "instagram": "@joao_silva",
  "grade": "2EM",
  "motivation": "Quero aprender diplomacia",
  "interests": "CS, MMA",
  "formato": "trio",
  "members": [
    {
      "name": "Maria Santos",
      "email": "maria@portalsesisp.org.br",
      "grade": "2EM",
      "instagram": "@maria_santos",
      "phone": "(11) 98888-1111"
    },
    {
      "name": "Pedro Costa",
      "email": "pedro@portalsesisp.org.br",
      "grade": "1EM",
      "instagram": "@pedro_costa",
      "phone": "(11) 97777-2222"
    }
  ]
}
```

Validações server-side:

| Validação | Regra |
|-----------|-------|
| `formato` | Obrigatório, deve ser `'individual'`, `'dupla'` ou `'trio'` |
| Membros | Se `dupla` → 1 membro; se `trio` → 2; se `individual` → 0 |
| Emails únicos | Email do inscrito + emails dos membros não podem repetir |
| Campos obrigatórios | `name`, `email`, `formato` sempre; membros: `name`, `email` |
| Email domain | Validar `@portalsesisp.org.br` |

Lógica:

```python
# Valida formato
formato = data.get('formato', 'individual')
members_data = data.get('members', [])

if formato == 'dupla' and len(members_data) != 1:
    return jsonify({'ok': False, 'error': 'Dupla requer exatamente 1 membro.'}), 400
if formato == 'trio' and len(members_data) != 2:
    return jsonify({'ok': False, 'error': 'Trio requer exatamente 2 membros.'}), 400

# Valida emails duplicados
all_emails = [data['email']] + [m['email'] for m in members_data]
if len(set(all_emails)) != len(all_emails):
    return jsonify({'ok': False, 'error': 'Emails duplicados entre os membros.'}), 400

# Cria inscrição
ins = Inscription(
    name=data['name'], email=data['email'],
    phone=data.get('phone', ''), grade=data.get('grade', ''),
    instagram=data.get('instagram', ''),
    motivation=data.get('motivation', ''),
    interests=data.get('interests', ''),
    formato=formato, type='delegate',
)
db.session.add(ins)
db.session.flush()

# Cria membros adicionais
for m in members_data:
    member = InscriptionMember(
        inscription_id=ins.id,
        name=m['name'], email=m['email'],
        grade=m.get('grade', ''), instagram=m.get('instagram', ''),
        phone=m.get('phone', ''),
    )
    db.session.add(member)

db.session.commit()
```

### 2.2 Atualizar `inscription_approve()` em `backend/routes/admin/inscriptions.py`

Ao aprovar inscrição com `formato != 'individual'`:

```python
from models.inscription_member import InscriptionMember
from models.user import User
from models.student import Student
from models.delegation import Delegation
from routes.admin._helpers import _ensure_participation_history

# 1. Coletar todos os participantes
participants = [{'name': ins.name, 'email': ins.email, 'phone': ins.phone}]
for m in ins.extra_members:
    participants.append({'name': m.name, 'email': m.email, 'phone': m.phone})

# 2. Para cada participante: criar conta se não existe
created_users = []
for p in participants:
    existing_user = User.query.filter_by(email=p['email']).first()
    if existing_user:
        student = Student.query.filter_by(email=p['email']).first()
        if not student:
            student = Student(user_id=existing_user.id, name=p['name'], email=p['email'])
            db.session.add(student)
            db.session.flush()
        created_users.append({'name': p['name'], 'email': p['email'], 'password': '(já possui conta)'})
        continue

    # Criar nova conta
    password = ''.join(secrets.choice(alphabet) for _ in range(10))
    user = User(name=p['name'], email=p['email'], role='student')
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    student = Student(user_id=user.id, name=p['name'], email=p['email'])
    db.session.add(student)
    db.session.flush()

    created_users.append({'name': p['name'], 'email': p['email'], 'password': password})

    # Enviar credenciais
    send_approval_email(...)

# 3. Criar Delegation vinculando todos os students
inscription_student = Student.query.filter_by(email=ins.email).first()
deleg = Delegation(
    inscription_id=ins.id,
    user_id=inscription_student.user_id,
    edition_year=datetime.now(timezone.utc).year,
    committee='',  # será atribuído depois pelo admin
    country='',    // será atribuído depois pelo admin
)
db.session.add(deleg)
db.session.flush()

for p in created_users:
    student = Student.query.filter_by(email=p['email']).first()
    if student:
        student.delegation_id = deleg.id
        student.convened = True
        _ensure_participation_history(student)

# 4. Flash com todas as credenciais
credenciais = '<br>'.join(
    f"• {u['name']}: {u['email']} | Senha: {u['password']}"
    for u in created_users
)
flash(f'✅ Inscrição aprovada! {len(created_users)} contas criadas:<br>{credenciais}', 'success')
```

---

## Fase 3 — Frontend: Redesign do Formulário

### 3.1 Layout do Form (`pages/faca-parte.html`)

```
┌──────────────────────────────────────────────────────┐
│  Como você vai participar?                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐     │
│  │     👤     │  │     👥     │  │    👥👥    │     │
│  │ Individual │  │   Dupla    │  │    Trio    │     │
│  └────────────┘  └────────────┘  └────────────┘     │
├──────────────────────────────────────────────────────┤
│  SEUS DADOS                                          │
│                                                      │
│  Nome completo *          ┌──────────────────────┐   │
│  Email educacional *      │ ______@portalesesisp │   │
│  Telefone                 ┌──────────────────────┐   │
│  Instagram                ┌──────────────────────┐   │
│  Turma/Série *            [ 6º ano ─── 3º EM   ]│   │
│  Por que deseja participar? *                     │   │
│  ┌──────────────────────────────────────────────┐│   │
│  │                                              ││   │
│  └──────────────────────────────────────────────┘│   │
├──────────────────────────────────────────────────────┤
│  COLEGA 1                          [ × remover ]    │
│  Nome completo *          ┌──────────────────────┐   │
│  Email educacional *      │ ______@portalesesisp │   │
│  Telefone                 ┌──────────────────────┐   │
│  Instagram                ┌──────────────────────┐   │
│  Turma/Série *            [ 6º ano ─── 3º EM   ]│   │
├──────────────────────────────────────────────────────┤
│  COLEGA 2                          [ × remover ]    │
│  Nome completo *          ┌──────────────────────┐   │
│  Email educacional *      │ ______@portalesesisp │   │
│  Telefone                 ┌──────────────────────┐   │
│  Instagram                ┌──────────────────────┐   │
│  Turma/Série *            [ 6º ano ─── 3º EM   ]│   │
├──────────────────────────────────────────────────────┤
│              [ Enviar Inscrição ]                    │
└──────────────────────────────────────────────────────┘
```

### 3.2 Comportamento JS

- Botões de formato são cards clicáveis com radio buttons escondidos
- Trocar formato:
  - `individual` → esconde todos os membros
  - `dupla` → mostra 1 membro
  - `trio` → mostra 2 membros
- Animação CSS: slide-down ao mostrar, slide-up ao esconder
- Validação JS antes do submit:
  - Emails repetidos → erro vermelho
  - Campos obrigatórios vazios → erro
  - Formato não selecionado → erro
- Email placeholder: `@portalsesisp.org.br`

### 3.3 Payload JS

```javascript
const formato = fd.get('formato'); // 'individual', 'dupla', 'trio'
const members = [];

if (formato === 'dupla' || formato === 'trio') {
  const m1 = {
    name: fd.get('member1_name'),
    email: fd.get('member1_email'),
    phone: fd.get('member1_phone'),
    instagram: fd.get('member1_instagram'),
    grade: fd.get('member1_grade'),
  };
  if (m1.name && m1.email) members.push(m1);
}

if (formato === 'trio') {
  const m2 = {
    name: fd.get('member2_name'),
    email: fd.get('member2_email'),
    phone: fd.get('member2_phone'),
    instagram: fd.get('member2_instagram'),
    grade: fd.get('member2_grade'),
  };
  if (m2.name && m2.email) members.push(m2);
}

const payload = {
  name:       fd.get('name'),
  email:      fd.get('email'),
  phone:      fd.get('phone') || '',
  instagram:  fd.get('instagram') || '',
  grade:      fd.get('grade') || '',
  motivation: fd.get('motivation') || '',
  interests:  fd.get('interests') || '',
  formato:    formato,
  members:    members,
  type:       'delegate',
};
```

---

## Fase 4 — Admin: Melhorar Lista de Inscrições

### 4.1 Atualizar `backend/templates/admin/inscriptions_list.html`

**Layout da tabela:**

| # | Inscrito | Formato | Membros | Status | Enviado | Ações |
|---|----------|---------|---------|--------|---------|-------|
| 12 | **João Silva**<br><small>joao@portalesesisp.org.br</small> | <span class="badge badge-purple">Trio</span> | 👥 Maria, Pedro | <span class="badge badge-yellow">Pendente</span> | 17/09/2026 | Ver · Aprovar · Rejeitar |
| 11 | **Ana Costa**<br><small>ana@portalesesisp.org.br</small> | <span class="badge badge-blue">Individual</span> | — | <span class="badge badge-green">Aprovado</span> | 17/09/2026 | Ver |

**Filtros:**
- Por status: Todas, Pendentes, Aprovadas, Rejeitadas (já existe)
- Por formato: Todos, Individual, Dupla, Trio (adicionar)

**Contadores no topo:**
- Total de inscrições
- Pendentes (amarelo)
- Aprovadas (verde)

### 4.2 Atualizar `backend/templates/admin/inscription_detail.html`

**Layout revisado:**

```
┌─────────────────────────────────────────────────────────────┐
│ ← Voltar para Inscrições                                    │
├────────────────────────────────┬────────────────────────────┤
│ DADOS DO INSCRITO              │ AÇÕES                      │
│                                │                            │
│ Nome: João Silva               │ [✅ Aprovar Inscrição]     │
│ Email: joao@portalesesisp.org  │ [❌ Rejeitar Inscrição]    │
│ Telefone: (11) 99999-0000      │                            │
│ Instagram: @joao_silva         │ Se aprovado:               │
│ Turma: 2º EM                   │ Credenciais geradas:       │
│ Formato: Trio                  │ • João: joao@... | Senha   │
│ Enviado: 17/09/2026            │ • Maria: maria@... | Senha │
│                                │ • Pedro: pedro@... | Senha │
│ Motivação:                     │                            │
│ "Quero aprender diplomacia..." │ Se rejeitado:              │
│                                │ Inscrição rejeitada.       │
├────────────────────────────────┤                            │
│ MEMBROS DO GRUPO               │                            │
│                                │                            │
│ ┌──────────────────────────┐   │                            │
│ │ 👥 Maria Santos          │   │                            │
│ │ maria@portalesesisp.org  │   │                            │
│ │ 2º EM · @maria_santos    │   │                            │
│ │ (11) 98888-1111          │   │                            │
│ └──────────────────────────┘   │                            │
│ ┌──────────────────────────┐   │                            │
│ │ 👥 Pedro Costa           │   │                            │
│ │ pedro@portalesesisp.org  │   │                            │
│ │ 1º EM · @pedro_costa     │   │                            │
│ │ (11) 97777-2222          │   │                            │
│ └──────────────────────────┘   │                            │
└────────────────────────────────┴────────────────────────────┘
```

---

## Fase 5 — Correções Paralelas (formulário atual)

### 5.1 Corrigir campos quebrados

- Remover campo `experience` do form (não é enviado nem armazenado)
- Corrigir `fd.get('motivation')` → enviar campo correto no form de voluntário
- Adicionar campos `availability` e `experience` ao payload do voluntário

### 5.2 Validações server-side

- Verificar se inscrições estão abertas (`EventConfig.inscricoes_abertas`) no endpoint `POST /api/inscricao`
- Adicionar rate limiting (ex: 1 inscrição por IP a cada 60 segundos)

### 5.3 Remover campos mortos do model

- `Inscription.school` → pode ser removido (nunca coletado)
- `Inscription.partner_name` → será substituído pelo relationship `extra_members`

---

## Arquivos a Criar/Modificar

| Arquivo | Ação | Fase |
|---------|------|------|
| `backend/models/inscription_member.py` | **Criar** — novo model | 1 |
| `backend/models/inscription.py` | **Modificar** — adicionar `instagram`, `formato`, relationship | 1 |
| `backend/routes/api.py` | **Modificar** — `api_inscricao()` aceitar members | 2 |
| `backend/routes/admin/inscriptions.py` | **Modificar** — aprovação cria students + delegation | 2 |
| `pages/faca-parte.html` | **Modificar** — redesign form + JS | 3 |
| `backend/templates/admin/inscriptions_list.html` | **Modificar** — layout melhorado | 4 |
| `backend/templates/admin/inscription_detail.html` | **Modificar** — mostrar membros | 4 |

---

## Ordem de Implementação

1. **Fase 1** — Models + Migration (base para tudo)
2. **Fase 2** — API + Aprovação (backend funcional)
3. **Fase 3** — Formulário frontend (usuário consegue inscrever)
4. **Fase 4** — Admin UI (admin consegue revisar)
5. **Fase 5** — Correções paralelas (limpeza)

---

## Riscos e Considerações

| Risco | Mitigação |
|-------|-----------|
| Migracao de dados (inscriptions existentes sem `formato`) | Default `'individual'` — dados existentes continuam funcionando |
| Emails duplicados entre inscritos | Validação server-side + tratamento de erro claro |
| Membros sem email @portalesesisp.org.br | Validar domínio no frontend e backend |
| Contas já existentes para membros | Reusar User existente, não criar duplicata |
| Senhas fracas no script `register_students.py` | Não alterar — é script de seed, não produção |
