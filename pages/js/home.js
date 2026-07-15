/* ============================================================
   SWDL — home.js
   Home page: carrega notícias e agenda via API,
   mantém fallback para conteúdo estático caso API offline.
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ── NOTÍCIAS ───────────────────────────────────────────────
  loadNoticias();

  async function loadNoticias(category = null) {
    const grid = document.getElementById('newsGrid');
    if (!grid) return;

    const params = category ? { category } : {};
    const news   = await SWDL_API.noticias({ ...params, limit: 3 });

    // Se a API não respondeu, mantém o HTML estático
    if (!news || news.length === 0) return;

    const catColors = {
      crise:    { bg: 'var(--red)',   label: '🚨 Crise' },
      oficial:  { bg: '#1A5276',      label: '📋 Oficial' },
      imprensa: { bg: 'var(--green)', label: '📰 Imprensa' },
      votacao:  { bg: 'var(--navy)',  label: '🗳️ Votação' },
    };

    const committeeColors = {
      cs:     'var(--red)',    mma:    'var(--green)',
      dhr:    '#8E44AD',       ecosoc: '#D4AC0D',
      disec:  '#E67E22',       oms:    '#2E86C1',
    };

    const emojis = { crise:'⚡', oficial:'📋', imprensa:'📰', votacao:'🗳️' };

    grid.innerHTML = news.map((n, i) => {
      const cat     = catColors[n.category] || catColors.oficial;
      const color   = committeeColors[n.committee] || 'var(--navy)';
      const emoji   = emojis[n.category] || '📋';
      const featured = i === 0 ? 'featured' : '';
      const link    = n.slug ? `${API_BASE}/noticia/${n.slug}` : '#';
      const imgHtml = n.cover_image
        ? `<img src="${n.cover_image}" alt="${n.title}" style="width:100%;height:100%;object-fit:cover;display:block">`
        : `<div class="news-img-icon">${emoji}</div>`;

      return `
        <article class="news-card ${featured}" data-cat="${n.category}">
          <a href="${link}">
            <div class="news-img" style="background:linear-gradient(135deg,${color},var(--navy));overflow:hidden">
              ${imgHtml}
            </div>
          </a>
          <div class="news-card-body">
            <span class="news-tag ${n.category}" style="background:${cat.bg}">${cat.label} — ${n.committee.toUpperCase()}</span>
            <a href="${link}" style="text-decoration:none;color:inherit">
              <h3>${n.title}</h3>
            </a>
            ${featured && n.excerpt ? `<p>${n.excerpt}</p>` : ''}
            <div class="news-meta">
              <div class="news-meta-left">
                <span class="dot" style="background:${color}"></span>
                ${n.committee.toUpperCase()}
              </div>
              <span class="news-time">${n.time_ago}</span>
            </div>
          </div>
        </article>`;
    }).join('');
  }

  // ── FILTROS DE NOTÍCIAS ────────────────────────────────────
  document.querySelectorAll('.filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const cat = btn.dataset.cat;
      loadNoticias(cat === 'all' ? null : cat);
    });
  });

  // ── AGENDA (strip da home) ─────────────────────────────────
  loadAgendaStrip();

  async function loadAgendaStrip() {
    const timeline = document.getElementById('timelineStrip');
    if (!timeline) return;

    const items = await SWDL_API.get('/agenda', { limit: 5 });
    if (!items || !items.length) return;

    timeline.innerHTML = items.slice(0, 5).map(item => {
      const isNow = item.status === 'now';
      return `
        <div class="timeline-item ${isNow ? 'active' : ''}">
          <div class="timeline-dot"></div>
          <span class="timeline-time">
            ${item.start_time}${item.end_time ? ' — ' + item.end_time : ''}
            ${isNow ? '<span class="timeline-badge">Agora</span>' : ''}
          </span>
          <div class="timeline-title">${item.title}</div>
          ${item.description ? `<div class="timeline-desc">${item.description.substring(0, 80)}...</div>` : ''}
        </div>`;
    }).join('');
  }

  // ── TICKER (notícias ao vivo) ──────────────────────────────
  loadTicker();

  async function loadTicker() {
    const tickerInner = document.getElementById('tickerInner');
    if (!tickerInner) return;

    const news = await SWDL_API.noticias({ limit: 8 });
    if (!news || !news.length) return;

    const items = [...news, ...news].map(n =>
      `<span class="ticker-item"><span class="sep">◆</span> <strong>${n.category.toUpperCase()} — ${n.committee.toUpperCase()}:</strong> ${n.title} <span class="sep">◆</span></span>`
    ).join('');
    tickerInner.innerHTML = items;
  }

  // ── FORMULÁRIO DE INSCRIÇÃO ────────────────────────────────
  const form        = document.getElementById('inscricaoForm');
  const formSuccess = document.getElementById('formSuccess');

  if (form) {
    form.addEventListener('submit', async e => {
      e.preventDefault();

      const submitBtn = form.querySelector('button[type="submit"]');
      submitBtn.textContent = 'Enviando...';
      submitBtn.disabled = true;

      const data = {
        name:         form.querySelector('[name="name"], input[placeholder*="nome"]')?.value || '',
        email:        form.querySelector('[type="email"]')?.value || '',
        grade:        form.querySelector('select')?.value || '',
        motivation:   form.querySelector('textarea')?.value || '',
        type:         'delegate',
      };

      const result = await SWDL_API.inscrever(data);

      // Sucesso (da API ou fallback visual)
      form.style.transition = 'opacity .3s';
      form.style.opacity    = '0';
      setTimeout(() => {
        form.style.display = 'none';
        if (formSuccess) {
          formSuccess.style.display  = 'block';
          formSuccess.style.opacity  = '0';
          setTimeout(() => {
            formSuccess.style.transition = 'opacity .4s';
            formSuccess.style.opacity    = '1';
          }, 20);
        }
      }, 300);
    });
  }

});