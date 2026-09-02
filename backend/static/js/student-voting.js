// ── SWDL — Votação do Aluno ────────────────────────────────
(function() {
  'use strict';
  let selectedChoice = null;

  window.selectVote = function(choice, el) {
    selectedChoice = choice;
    const colors = {favor:'var(--green)', contra:'var(--red)', abstencao:'var(--slate)'};
    document.querySelectorAll('.v-opt').forEach(function(o) {
      o.classList.remove('v-opt--selected');
      o.querySelector('.v-check').textContent = '';
    });
    el.classList.add('v-opt--selected');
    el.querySelector('.v-check').textContent = '✓';
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
        const icons = {favor:'✅', contra:'❌', abstencao:'🤝'};
        const labels = {favor:'A Favor registrado!', contra:'Contra registrado!', abstencao:'Abstenção registrada!'};
        document.getElementById('voteOptions').style.display = 'none';
        btn.style.display = 'none';
        const result = document.getElementById('voteResult');
        result.style.display = 'block';
        document.getElementById('voteResultIcon').textContent = icons[selectedChoice];
        document.getElementById('voteResultTitle').textContent = labels[selectedChoice];
      } else {
        btn.disabled = false;
        btn.textContent = 'Confirmar Voto';
        alert(data.error || 'Erro ao votar.');
      }
    } catch (e) {
      btn.disabled = false;
      btn.textContent = 'Confirmar Voto';
      alert('Erro de conexão. Tente novamente.');
    }
  };
})();
