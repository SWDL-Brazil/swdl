# SWDL Web — Next.js + Tailwind CSS

Site público da SWDL — SESI World Diplomacy League, reconstruído com Next.js 14 e Tailwind CSS.

## Stack

- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS 3.4
- **Animações:** Framer Motion
- **Globo 3D:** React Three Fiber + Drei
- **i18n:** next-intl (9 idiomas)
- **Formulários:** React Hook Form + Zod
- **Icons:** Lucide React
- **Deploy:** Vercel

## Estrutura

```
swdl-web/
├── app/                    # Rotas Next.js
│   ├── [locale]/          # Rotas com i18n
│   │   ├── page.tsx       # Home
│   │   ├── noticias/      # Notícias
│   │   ├── comites/       # Comitês
│   │   ├── agenda/        # Agenda
│   │   ├── sobre/         # Sobre
│   │   ├── faca-parte/    # Inscrição
│   │   └── ...            # Páginas legais
│   └── layout.tsx         # Root layout
├── components/             # Componentes React
│   ├── ui/                # Componentes atômicos
│   ├── layout/            # Navbar, Footer, Ticker
│   ├── home/              # Hero, Globe3D, Stats
│   └── ...                # Outros
├── lib/                   # Utilitários
│   ├── api.ts             # API client
│   └── utils.ts           # Helpers
├── messages/              # Traduções (9 idiomas)
└── public/                # Assets estáticos
```

## Setup

```bash
# Instalar dependências
npm install

# Rodar em desenvolvimento
npm run dev

# Build para produção
npm run build

# Iniciar servidor de produção
npm start
```

## Variáveis de Ambiente

```env
NEXT_PUBLIC_API_URL=https://swdl.onrender.com/api
```

## Deploy no Vercel

1. Conectar o repo ao Vercel
2. Configurar `NEXT_PUBLIC_API_URL` nas variáveis de ambiente
3. Deploy automático a cada push no `main`

## Backend

O backend Flask continua rodando no Render:
- URL: `https://swdl.onrender.com`
- CORS atualizado para aceitar `swdl.vercel.app`
