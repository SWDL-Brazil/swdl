// ── SWDL — Votação do Aluno ────────────────────────────────
(function() {
  'use strict';
  let selectedChoice = null;
  const ico = (n, cls) => (window.stIcon ? window.stIcon(n, cls) : '');

  window.selectVote = function(choice, el) {
    selectedChoice = choice;
    const colors = {favor:'var(--green)', contra:'var(--red)', abstencao:'var(--slate)'};
    document.querySelectorAll('.v-opt').forEach(function(o) {
      o.classList.remove('v-opt--selected');
      o.querySelector('.v-check').innerHTML = '';
    });
    el.classList.add('v-opt--selected');
    el.querySelector('.v-check').innerHTML = ico('check');
    document.getElementById('submitVote').disabled = false;
  };

  window.submitVote = async function(sessionId) {
    if (!selectedChoice) return;
    const btn = document.getElementById('submitVote');
    btn.disabled = true;
    btn.textContent = 'Registrando...';
    try {
      const res = await fetch('/api/votar', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({session_id: sessionId, choice: selectedChoice})
      });
      const data = await res.json();
      if (data.ok) {
        const icons = {favor:'check-circle', contra:'x-circle', abstencao:'minus-circle'};
        const labels = {favor:'A Favor registrado!', contra:'Contra registrado!', abstencao:'Abstenção registrada!'};
        document.getElementById('voteOptions').style.display = 'none';
        btn.style.display = 'none';
        const result = document.getElementById('voteResult');
        result.style.display = 'block';
        document.getElementById('voteResultIcon').innerHTML = ico(icons[selectedChoice], 'st-ico-xl');
        document.getElementById('voteResultTitle').textContent = labels[selectedChoice];
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
