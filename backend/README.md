# SWDL — Backend (Flask)

## Setup rápido

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Rodar o servidor
python app.py
```

O servidor sobe em **http://localhost:5000**

## Login padrão (criado automaticamente)
- **URL:** http://localhost:5000/admin/login
- **E-mail:** admin@swdl.com
- **Senha:** swdl2025

> ⚠️ Troque a senha após o primeiro acesso em produção.

## Estrutura

```
backend/
├── app.py              # Ponto de entrada
├── config.py           # Configurações (DB, uploads, etc.)
├── extensions.py       # db, login_manager
├── requirements.txt
│
├── models/
│   ├── user.py         # Usuários e permissões
│   ├── news.py         # Notícias
│   ├── agenda.py       # Itens da agenda
│   ├── inscription.py  # Inscrições de candidatos
│   └── delegation.py   # Designação de países
│
├── routes/
│   ├── auth.py         # Login / logout
│   ├── admin.py        # Painel admin (todas as telas)
│   └── api.py          # API JSON para o front-end
│
└── templates/
    └── admin/
        ├── base.html              # Layout com sidebar
        ├── login.html
        ├── dashboard.html
        ├── news_list.html
        ├── news_form.html
        ├── agenda_list.html
        ├── agenda_form.html
        ├── inscriptions_list.html
        ├── inscription_detail.html
        ├── delegations_list.html
        └── delegation_assign.html
```

## API Endpoints (consumidos pelo front-end)

| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/api/noticias` | Lista notícias publicadas |
| GET | `/api/agenda` | Lista itens da agenda |
| GET | `/api/agenda/agora` | Atividade atual + próxima |
| POST | `/api/inscricao` | Recebe inscrição do site |
| GET | `/api/status` | Estado do evento (crise ativa?) |

## Próximos passos (Fase 3)
- Dashboard do Delegado (login, aceite de país, upload DPO)
- Sistema de votação em tempo real (WebSockets via Flask-SocketIO)
