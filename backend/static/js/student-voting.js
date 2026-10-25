// ── SWDL — Votação do Aluno ────────────────────────────────
// IDs são por sessão (voteOptions-<id>, submitVote-<id>, ...) porque a
// página renderiza 1 card por votação aberta — ids únicos globais quebram
// quando há mais de uma votação em pauta.
(function() {
  'use strict';
  const selections = {};
  const ico = (n, cls) => (window.stIcon ? window.stIcon(n, cls) : '');
  const $ = (id) => document.getElementById(id);

  window.selectVote = function(sessionId, choice, el) {
    selections[sessionId] = choice;
    const group = $('voteOptions-' + sessionId);
    if (group) {
      group.querySelectorAll('.v-opt').forEach(function(o) {
        o.classList.remove('v-opt--selected');
        const chk = o.querySelector('.v-check');
        if (chk) chk.innerHTML = '';
      });
    }
    el.classList.add('v-opt--selected');
    const check = el.querySelector('.v-check');
    if (check) check.innerHTML = ico('check');
    const btn = $('submitVote-' + sessionId);
    if (btn) btn.disabled = false;
  };

  window.submitVote = async function(sessionId) {
    const choice = selections[sessionId];
    if (!choice) return;
    const btn = $('submitVote-' + sessionId);
    if (!btn) return;
    btn.disabled = true;
    btn.textContent = 'Registrando...';
    try {
      const res = await fetch('/api/votar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({session_id: sessionId, choice: choice})
      });
      const data = await res.json();
      if (data.ok) {
        const icons = {favor:'check-circle', contra:'x-circle', abstencao:'minus-circle'};
        const labels = {favor:'A Favor registrado!', contra:'Contra registrado!', abstencao:'Abstenção registrada!'};
        const options = $('voteOptions-' + sessionId);
        if (options) options.style.display = 'none';
        btn.style.display = 'none';
        const result = $('voteResult-' + sessionId);
        if (result) result.style.display = 'block';
        const rIcon = $('voteResultIcon-' + sessionId);
        if (rIcon) rIcon.innerHTML = ico(icons[choice], 'st-ico-xl');
        const rTitle = $('voteResultTitle-' + sessionId);
        if (rTitle) rTitle.textContent = labels[choice];
      } else {
        btn.disabled = false;
        btn.textContent = 'Confirmar Voto';
        if (window.showToast) showToast('Erro ao votar', data.error || 'Tente novamente.', {variant:'error'});
        else alert(data.error || 'Erro ao votar.');
      }
    } catch (e) {
      btn.disabled = false;
      btn.textContent = 'Confirmar Voto';
      if (window.showToast) showToast('Erro de conexão', 'Tente novamente.', {variant:'error'});
      else alert('Erro de conexão. Tente novamente.');
    }
  };
})();
