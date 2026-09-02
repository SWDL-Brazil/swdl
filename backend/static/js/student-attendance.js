// ── SWDL — Presença do Aluno ───────────────────────────────
(function() {
  'use strict';

  // Triagem de infraestrutura
  var triagem = document.getElementById('deviceTriagem');
  if (triagem) {
    var warnings = [];
    if (window.innerWidth < 768 || ('ontouchstart' in window)) {
      warnings.push('📱 Dispositivo móvel detectado');
    }
    if (!navigator.onLine) {
      warnings.push('🔴 Sem conexão com a internet');
    }
    if (window.innerWidth < 480) {
      warnings.push('📏 Tela muito pequena — use o Modo Rápido para facilitar');
    }
    if (warnings.length) {
      triagem.style.display = 'flex';
      triagem.style.alignItems = 'center';
      triagem.style.gap = '8px';
      triagem.style.background = 'rgba(212,131,15,.08)';
      triagem.style.border = '1px solid rgba(212,131,15,.2)';
      triagem.style.color = '#856404';
      triagem.innerHTML = '🔍 ' + warnings.join(' · ');
    }
    if (window.innerWidth < 768 && ('ontouchstart' in window)) {
      var card = document.getElementById('presenceCard');
      if (card) {
        var hint = document.createElement('div');
        hint.style.cssText = 'font-size:11px;color:var(--muted);margin-top:8px';
        hint.textContent = '💡 Dispositivo touch detectado — use o Modo Rápido abaixo';
        card.querySelector('.card-body').appendChild(hint);
      }
    }
  }

  // Toggle modo rápido
  window.toggleQuickMode = function() {
    var panel = document.getElementById('quickModePanel');
    if (!panel) return;
    if (panel.style.display === 'none' || panel.style.display === '') {
      panel.style.display = 'block';
      panel.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } else {
      panel.style.display = 'none';
    }
  };

  // Quick mode form submission
  document.addEventListener('DOMContentLoaded', function() {
    var quickForm = document.getElementById('quickPresenceForm');
    if (quickForm) {
      quickForm.addEventListener('submit', function(e) {
        e.preventDefault();
        var form = e.target;
        fetch(form.action || window.location.href, {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: new URLSearchParams(new FormData(form))
        }).then(function(resp) {
          if (resp.redirected) {
            window.location.href = resp.url;
          } else {
            window.location.href = quickForm.dataset.logoutUrl || '/student/logout';
          }
        }).catch(function() {
          window.location.href = quickForm.dataset.logoutUrl || '/student/logout';
        });
      });
    }
  });
})();
