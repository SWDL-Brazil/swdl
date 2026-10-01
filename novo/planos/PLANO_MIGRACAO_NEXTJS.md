# Plano de Migração: SWDL → Next.js + Tailwind CSS

## Visão Geral

Migrar o site público estático (HTML/CSS/JS puro) para **Next.js 14** com **Tailwind CSS**, mantendo o backend Flask existente. O objetivo é criar uma experiência "WOW" com design premium, animações suaves e um globo 3D interativo.

---

## Por que Next.js + Tailwind?

| Atual (HTML/CSS/JS) | Futuro (Next.js + Tailwind) |
|---|---|
| 10 arquivos HTML duplicados | Componentes React reutilizáveis |
| CSS manual (~2500 linhas) | Tailwind utilities + design tokens |
| i18n.js customizado (794 linhas) | `next-intl` com SSR |
| Fetch client-side apenas | Server Components + ISR |
| Deploy manual Firebase | Auto-deploy Vercel |
| Sem type safety | TypeScript completo |

---

## Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Framework | Next.js 14 (App Router) |
| Styling | Tailwind CSS 3.4 |
| Animações | Framer Motion + Spline (globo 3D) |
| i18n | next-intl (9 idiomas) |
| Formulários | React Hook Form + Zod |
| Icons | Lucide React |
| Deploy | Vercel (recomendado) |
| Backend | Flask no Render (sem mudança) |

---

## Deploy: Vercel (Recomendado)

### Por que Vercel?
- **Otimizado para Next.js** — criado pelos mesmos desenvolvedores
- **Edge Functions** — middleware de locale rodando na edge
- **ISR (Incremental Static Regeneration)** — páginas estáticas com revalidação automática
- **Preview Deployments** — cada PR gera uma URL de preview
- **Analytics** — web vitals integrados
- **Gratuito para projetos pessoais** — 100GB de bandwidth/mês

### Fluxo de Deploy
```
GitHub (repo swdl-web)
    │
    ├── main branch push
    │
    └── Vercel (auto-deploy)
        ├── Build: next build
        ├── Edge: middleware.ts (locale detection)
        ├── ISR: /noticias, /agenda (revalidate: 60s)
        ├── SSG: /comites, /sobre, /aviso-legal (static)
        └── API Routes: /api/* (se necessário)
```

### Domínio
- Produção: `swdl.vercel.app` (ou domínio customizado)
- Preview: `swdl-git-branch.vercel.app`

---

## Estrutura do Projeto

```
swdl-web/                        # Diretório raiz do projeto
├── app/
│   ├── [locale]/                # Rotas com i18n
│   │   ├── layout.tsx           # Layout raiz (Navbar + Footer)
│   │   ├── page.tsx             # Home (/)
│   │   ├── noticias/
│   │   │   └── page.tsx         # Notícias
│   │   ├── comites/
│   │   │   └── page.tsx         # Comitês/Temas
│   │   ├── agenda/
│   │   │   └── page.tsx         # Agenda
│   │   ├── sobre/
│   │   │   └── page.tsx         # Sobre
│   │   ├── faca-parte/
│   │   │   └── page.tsx         # Inscrição
│   │   ├── aviso-legal/
│   │   │   └── page.tsx         # Aviso legal
│   │   ├── privacidade/
│   │   │   └── page.tsx         # Privacidade
│   │   └── termos/
│   │       └── page.tsx         # Termos
│   ├── layout.tsx               # Root layout
│   ├── not-found.tsx            # 404
│   └── globals.css              # Tailwind imports
│
├── components/
│   ├── ui/                      # Componentes atômicos
│   │   ├── Button.tsx
│   │   ├── Badge.tsx
│   │   ├── Card.tsx
│   │   └── Container.tsx
│   ├── layout/
│   │   ├── Navbar.tsx
│   │   ├── Footer.tsx
│   │   ├── Ticker.tsx
│   │   └── CrisisBanner.tsx
│   ├── home/
│   │   ├── Hero.tsx
│   │   ├── Globe3D.tsx          # Globo 3D com Spline/Three.js
│   │   ├── Stats.tsx
│   │   ├── NewsGrid.tsx
│   │   ├── AgendaStrip.tsx
│   │   └── CommitteesPreview.tsx
│   ├── noticias/
│   │   ├── NewsCard.tsx
│   │   ├── CategoryPanel.tsx
│   │   └── NewsDetail.tsx
│   ├── agenda/
│   │   ├── NowCard.tsx
│   │   ├── DayTabs.tsx
│   │   └── Timeline.tsx
│   ├── comites/
│   │   └── CommitteeCard.tsx
│   └── faca-parte/
│       ├── FormatSelector.tsx
│       ├── DelegateForm.tsx
│       └── VolunteerForm.tsx
│
├── lib/
│   ├── api.ts                   # API client
│   ├── i18n.ts                  # Config next-intl
│   └── utils.ts                 # Helpers
│
├── messages/                    # Traduções
│   ├── pt-BR.json
│   ├── en.json
│   ├── es.json
│   ├── fr.json
│   ├── de.json
│   ├── it.json
│   ├── nl.json
│   ├── id.json
│   └── ms.json
│
├── public/
│   ├── icons/
│   ├── img/
│   └── PDF/
│
├── tailwind.config.ts
├── next.config.ts
├── middleware.ts
├── package.json
└── tsconfig.json
```

---

## Design System (Tailwind)

### Paleta de Cores
```ts
colors: {
  navy:      '#0D1B2A',   // Primária
  navyDark:  '#071018',   // Navy escuro
  navyMid:   '#1B2838',   // Navy médio
  gold:      '#C9A84C',   // Destaque
  goldLight: '#DFC06B',   // Gold claro
  slate:     '#8B92A5',   // Secundária
  surface:   '#FAFAF8',   // Background
  surfaceAlt:'#F4F3F0',   // Background alternado
}
```

### Tipografia
- **Display:** Playfair Display (títulos)
- **Body:** DM Sans (corpo)
- **Mono:** DM Mono (labels/tags)

### Sombras
```ts
shadow: {
  card:      '0 1px 3px rgba(0,0,0,0.06), 0 4px 12px rgba(0,0,0,0.04)',
  elevated:  '0 8px 24px rgba(0,0,0,0.08)',
  glow:      '0 0 40px rgba(201,168,76,0.15)',
}
```

---

## Globo 3D

### Opção Recomendada: Spline Runtime
- **Spline** (spline.design) para criar o globo 3D
- **@splinetool/react-spline** para importar no React
- Globo com rotação suave, países destacados em gold
- Alternativa: Three.js com `react-three-fiber` se quiser controle total

### Integração
```tsx
// components/home/Globe3D.tsx
'use client';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Sphere } from '@react-three/drei';

export function Globe3D() {
  return (
    <Canvas>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <Sphere args={[1, 64, 64]}>
        <meshStandardMaterial color="#0D1B2A" wireframe />
      </Sphere>
      <OrbitControls enableZoom={false} autoRotate autoRotateSpeed={0.5} />
    </Canvas>
  );
}
```

---

## Endpoints da API (Backend Flask)

O backend não muda. Apenas CORS é atualizado.

| Endpoint | Método | Uso no Site |
|---|---|---|
| `/api/noticias` | GET | Página de notícias |
| `/api/noticia/<slug>` | GET | Detalhe da notícia |
| `/api/categorias` | GET | Filtros de categoria |
| `/api/agenda` | GET | Página de agenda |
| `/api/agenda/agora` | GET | Card "Agora" |
| `/api/periods` | GET | Períodos do evento |
| `/api/comites` | GET | Board de comitês |
| `/api/ticker` | GET | Barra de ticker |
| `/api/status` | GET | Banner de crise |
| `/api/config` | GET | Status das inscrições |
| `/api/bandeira` | GET | Bandeiras de países |
| `POST /api/inscricao` | POST | Formulário de inscrição |

---

## i18n (9 Idiomas)

### Idiomas Suportados
| Código | Idioma |
|---|---|
| `pt-BR` | Português (Brasil) — padrão |
| `en` | English |
| `es` | Español |
| `fr` | Français |
| `de` | Deutsch |
| `it` | Italiano |
| `nl` | Nederlands |
| `id` | Bahasa Indonesia |
| `ms` | Bahasa Melayu |

### URLs
- `/pt-BR/noticias` → `/en/news` → `/es/noticias`
- Middleware detecta `Accept-Language` e redireciona

### Extração
~400 chaves serão extraídas do `i18n.js` atual para JSON files.

---

## Animações (Framer Motion)

- **Scroll Reveal:** Elementos surgem com fade + slide ao entrar no viewport
- **Page Transitions:** Transições suaves entre páginas
- **Hover Effects:** Cards com elevação suave
- **Counter Animation:** Números animados nas stats
- **Ticker:** Scroll infinito com velocidade constante
- **Globe:** Rotação contínua suave

---

## Mudanças no Backend

### CORS (backend/app.py)
```python
CORS(app, origins=[
    'https://swdl-5a3fa.web.app',
    'https://swdl-5a3fa.firebaseapp.com',
    'https://swdl.vercel.app',
    'https://swdl-*.vercel.app',
])
```

---

## Fases de Implementação

| Fase | Descrição | Dependências |
|---|---|---|
| 1 | Setup Next.js + Tailwind + TS | Nenhuma |
| 2 | Design tokens + globals.css | Fase 1 |
| 3 | API client + types | Fase 1 |
| 4 | Layout (Navbar, Footer, Ticker, CrisisBanner) | Fases 2, 3 |
| 5 | Homepage (Hero, Globe 3D, Stats, News, Agenda) | Fase 4 |
| 6 | Páginas interiores | Fases 3, 4 |
| 7 | Formulário de inscrição | Fase 3 |
| 8 | Páginas legais | Fase 4 |
| 9 | i18n (next-intl) | Fases 4-8 |
| 10 | Animações Framer Motion | Fases 4-8 |
| 11 | Deploy Vercel + CORS | Todas |

---

## Arquivos de Referência

| Arquivo | Propósito |
|---|---|
| `pages/css/variables.css` | Design tokens atuais |
| `pages/js/i18n.js` | Traduções (~400 chaves) |
| `pages/js/api.js` | API client atual |
| `pages/js/main.js` | Lógica global |
| `pages/js/home.js` | Lógica da homepage |
| `backend/routes/api.py` | Endpoints da API |
| `backend/app.py` | CORS config |

---

## Status

- [ ] Fase 1: Setup do projeto
- [ ] Fase 2: Design tokens
- [ ] Fase 3: API client
- [ ] Fase 4: Layout components
- [ ] Fase 5: Homepage
- [ ] Fase 6: Páginas interiores
- [ ] Fase 7: Formulário inscrição
- [ ] Fase 8: Páginas legais
- [ ] Fase 9: i18n
- [ ] Fase 10: Animações
- [ ] Fase 11: Deploy
