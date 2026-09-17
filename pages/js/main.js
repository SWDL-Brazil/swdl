/* ============================================================
   SWDL — main.js
   Scripts globais: navbar, scroll reveal, counter, crisis
   ============================================================ */

document.addEventListener('DOMContentLoaded', () => {

  // ── NAVBAR SCROLL ──────────────────────────────────────────
  const nav = document.querySelector('nav.swdl-nav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 40);
    });
  }

  // ── ACTIVE NAV LINK ────────────────────────────────────────
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href && (currentPage === href || currentPage === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });

  // ── MOBILE HAMBURGER ───────────────────────────────────────
  const hamburger = document.querySelector('.nav-hamburger');
  const navLinks  = document.querySelector('.nav-links');
  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      navLinks.classList.toggle('open');
    });
  }

  // ── SCROLL REVEAL ──────────────────────────────────────────
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        entry.target.querySelectorAll('[data-count]').forEach(startCounter);
        if (entry.target.dataset.count !== undefined) startCounter(entry.target);
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));

  // ── COUNTER ANIMATION ──────────────────────────────────────
  function startCounter(el) {
    const target   = parseInt(el.dataset.count);
    const duration = 1800;
    const start    = performance.now();
    const tick = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      const ease     = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(ease * target);
      if (progress < 1) requestAnimationFrame(tick);
      else el.textContent = target;
    };
    requestAnimationFrame(tick);
  }

  document.querySelectorAll('[data-count]').forEach(el => {
    if (el.getBoundingClientRect().top < window.innerHeight) startCounter(el);
  });

  // ── SMOOTH ANCHOR SCROLL ───────────────────────────────────
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', e => {
      const target = document.querySelector(anchor.getAttribute('href'));
      if (target) {
        e.preventDefault();
        window.scrollTo({
          top: target.getBoundingClientRect().top + window.scrollY - 84,
          behavior: 'smooth'
        });
      }
    });
  });

  // ── CENTRALIZED EMAIL ─────────────────────────────────────
  if (typeof SWDL_CONFIG !== 'undefined' && SWDL_CONFIG.email) {
    document.querySelectorAll('a[href^="mailto:"]').forEach(el => {
      el.href = 'mailto:' + SWDL_CONFIG.email;
    });
    document.querySelectorAll('[data-i18n="footer.email_link"]').forEach(el => {
      el.textContent = SWDL_CONFIG.email;
    });
  }

  // ── CRISIS BANNER ──────────────────────────────────────────
  if (typeof SWDL_API !== 'undefined') {
    async function loadCrisisBanner() {
      const data = await SWDL_API.status();
      const banner = document.getElementById('crisis-banner');
      if (!banner) return;
      if (data && data.crisis_active && data.crisis_message) {
        const textEl = banner.querySelector('.crisis-text');
        if (textEl) textEl.textContent = '🚨 CRISE: ' + data.crisis_message;
        banner.classList.add('active');
        banner.style.display = 'flex';
      } else {
        banner.classList.remove('active');
        banner.style.display = 'none';
      }
      document.body.classList.toggle('crisis-active', data && data.crisis_active);
    }
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.crisis-close');
      if (btn) {
        document.getElementById('crisis-banner')?.classList.remove('active');
        document.body.classList.remove('crisis-active');
      }
    });
    loadCrisisBanner();
    setInterval(loadCrisisBanner, 60000);
  }

});