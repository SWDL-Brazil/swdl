/* =============================================================
   SWDL Telao JavaScript
   IIFE - uses const/let, textContent where possible
   ============================================================= */
(function () {
  'use strict';

  const $id = (id) => document.getElementById(id);
  function esc(s) {
    if (!s) return '';
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  const SCREENS = [
    'idleScreen','voteScreen','resultScreen','chamadaScreen',
    'speechScreen','speakerQueueScreen','motionScreen',
    'resolutionScreen'
  ];

  /* ---- Clock ---- */
  setInterval(() => {
    const el = $id('clock');
    if (el) el.textContent = new Date().toLocaleTimeString('pt-BR');
  }, 1000);

  /* ---- Utility ---- */
  function show(id) {
    SCREENS.forEach((s) => {
      const el = $id(s);
      if (el) el.style.display = (s === id) ? 'flex' : 'none';
    });
    const ov = $id('oradores-overlay');
    if (ov && id !== 'idleScreen') ov.remove();
  }

  function buildTicker(items) {
    const inner = $id('tickerInner');
    if (!inner) return;
    const html = [...items, ...items]
      .map((t) => `<span class="t-ticker-item">${t}</span><span class="t-ticker-sep"> \u25C6 </span>`)
      .join('');
    inner.innerHTML = html;
  }

  function flashScreen() {
    const el = $id('screenFlash');
    if (!el) return;
    el.style.opacity = '0.18';
    setTimeout(() => { el.style.opacity = '0'; }, 200);
  }

  function updateConnectionDot(connected) {
    let dot = $id('wsIndicator');
    if (!dot) {
      dot = document.createElement('div');
      dot.id = 'wsIndicator';
      dot.style.cssText = 'position:fixed;bottom:12px;right:12px;width:10px;height:10px;border-radius:50%;z-index:999;transition:background .3s;';
      document.body.appendChild(dot);
    }
    dot.style.background = connected ? '#2ECC71' : '#E74C3C';
  }

  /* ---- Debate Timer (server-synced) ---- */
  let debateSec = 0, debateRunning = false, debateInterval = null;

  function renderDebate() {
    const h = String(Math.floor(debateSec / 3600)).padStart(2, '0');
    const m = String(Math.floor((debateSec % 3600) / 60)).padStart(2, '0');
    const s = String(debateSec % 60).padStart(2, '0');
    const el = $id('debateTime');
    if (el) el.textContent = `${h}:${m}:${s}`;
  }

  function syncDebateTimer(data) {
    debateSec = data.elapsed || 0;
    debateRunning = data.running || false;
    if (debateRunning) {
      clearInterval(debateInterval);
      debateInterval = setInterval(() => { debateSec++; renderDebate(); }, 1000);
    } else {
      clearInterval(debateInterval);
    }
    renderDebate();
  }

  window.toggleDebate = function () {
    if (debateRunning) {
      socket.emit('debate_timer_pause', {});
    } else {
      socket.emit('debate_timer_start', {});
    }
  };

  window.resetDebate = function () {
    socket.emit('debate_timer_reset', {});
  };

  /* ---- Speech Timer ---- */
  let speechTotal = 90, speechRem = 0, speechRunning = false, speechInterval = null;

  function playSirene() {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      const osc = ctx.createOscillator();
      const g = ctx.createGain();
      osc.type = 'sawtooth';
      osc.connect(g);
      g.connect(ctx.destination);
      g.gain.setValueAtTime(0.3, ctx.currentTime);
      g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 2);
      osc.frequency.setValueAtTime(440, ctx.currentTime);
      osc.frequency.linearRampToValueAtTime(880, ctx.currentTime + 0.3);
      osc.frequency.linearRampToValueAtTime(440, ctx.currentTime + 0.6);
      osc.frequency.linearRampToValueAtTime(880, ctx.currentTime + 0.9);
      osc.frequency.linearRampToValueAtTime(440, ctx.currentTime + 1.2);
      osc.frequency.linearRampToValueAtTime(880, ctx.currentTime + 1.5);
      osc.start();
      osc.stop(ctx.currentTime + 2);
    } catch (e) { /* silent */ }
  }

  function renderSpeech() {
    const el = $id('speechTimeCenter');
    const bar = $id('speechBarCenter');
    if (!el || !bar) return;
    const pct = speechRem / speechTotal;
    const m = String(Math.floor(speechRem / 60)).padStart(2, '0');
    const s = String(speechRem % 60).padStart(2, '0');
    el.textContent = `${m}:${s}`;
    if (speechRem <= 0) {
      el.className = 'speech-time idle';
    } else if (speechRem <= 10) {
      el.className = 'speech-time urgent';
      bar.style.background = 'var(--red-l)';
    } else if (speechRem <= speechTotal * 0.3) {
      el.className = 'speech-time warning';
      bar.style.background = 'var(--gold)';
    } else {
      el.className = 'speech-time running';
      bar.style.background = 'var(--green-l)';
    }
    bar.style.transform = `scaleX(${Math.max(0, pct)})`;
  }

  function startSpeech(secs) {
    clearInterval(speechInterval);
    speechTotal = secs || 90;
    speechRem = speechTotal;
    speechRunning = true;
    renderSpeech();
    show('speechScreen');
    speechInterval = setInterval(() => {
      if (!speechRunning) return;
      speechRem--;
      renderSpeech();
      if (speechRem <= 0) {
        clearInterval(speechInterval);
        speechRunning = false;
        playSirene();
        flashScreen();
      }
    }, 1000);
  }

  function resetSpeech() {
    clearInterval(speechInterval);
    speechRunning = false;
    speechRem = 0;
    const el = $id('speechTimeCenter');
    const bar = $id('speechBarCenter');
    if (el) { el.textContent = '--:--'; el.className = 'speech-time'; }
    if (bar) { bar.style.transform = 'scaleX(0)'; bar.style.background = 'var(--green-l)'; }
    show('idleScreen');
  }

  window.startSpeechTimer = function (duration) { startSpeech(duration || 90); };
  window.stopSpeechTimer = function () { clearInterval(speechInterval); speechRunning = false; };
  window.resetSpeechTimer = function () { resetSpeech(); };

  /* ---- Vote Timer ---- */
  const CIRC = 226;
  let voteInterval = null, voteRem = 0, voteTotal = 120, currentSession = null;

  function renderVoteTimer() {
    const mm = String(Math.floor(voteRem / 60)).padStart(2, '0');
    const ss = String(voteRem % 60).padStart(2, '0');
    const numEl = $id('timerNum');
    const arc = $id('timerArc');
    if (numEl) numEl.textContent = `${mm}:${ss}`;
    if (arc) {
      arc.style.strokeDashoffset = CIRC * (1 - voteRem / voteTotal);
      if (voteRem <= 10) arc.style.stroke = 'var(--red-l)';
      else if (voteRem <= 30) arc.style.stroke = '#E67E22';
      else arc.style.stroke = 'var(--gold)';
    }
  }

  function startVoteTimer(secs) {
    clearInterval(voteInterval);
    voteTotal = secs || 120;
    voteRem = voteTotal;
    renderVoteTimer();
    voteInterval = setInterval(() => {
      if (voteRem > 0) {
        voteRem--;
        renderVoteTimer();
      } else {
        clearInterval(voteInterval);
        if (currentSession) {
          fetch(`/api/vote/${currentSession.id}/auto_close`, { method: 'POST' });
          showResult(currentSession);
        }
      }
    }, 1000);
  }

  /* ---- Vote rendering ---- */
  function loadSession(session) {
    currentSession = session;
    show('voteScreen');
    const titleEl = $id('qTitle');
    const descEl = $id('qDesc');
    const ct = $id('committeeTag');
    if (titleEl) titleEl.textContent = session.title || '\u2014';
    if (descEl) descEl.textContent = session.description || '';
    if (ct) {
      ct.textContent = (session.committee || 'GERAL').toUpperCase();
      ct.style.display = 'block';
    }
    ['favor', 'contra', 'abstencao'].forEach((k) => {
      const el = $id('list-' + k);
      if (el) el.innerHTML = '';
      const cnt = $id('cnt-' + k);
      if (cnt) cnt.textContent = '0';
    });
    if (session.votes) session.votes.forEach(addVote);
    if (session.counts) updateCounts(session.counts);
    startVoteTimer(session.remaining_sec != null ? session.remaining_sec : (session.duration_sec || 120));
  }

  function renderVotes(data) {
    ['favor', 'contra', 'abstencao'].forEach((k) => {
      const el = $id('list-' + k);
      if (el) el.innerHTML = '';
    });
    if (data.votes) data.votes.forEach(addVote);
    if (data.counts) updateCounts(data.counts);
  }

  function addVote(vote) {
    const listEl = $id('list-' + vote.choice);
    if (!listEl) return;
    const item = document.createElement('div');
    item.className = 't-country-item';
    let flag = '';
    if (vote.flag_url && vote.flag_url.trim()) {
      flag = `<img class="t-flag-img" src="${vote.flag_url}" onerror="this.style.display='none'" alt="">`;
    } else if (vote.flag) {
      flag = `<span class="t-flag-emoji">${vote.flag}</span>`;
    } else {
      flag = '<span class="t-flag-emoji">\uD83C\uDF0D</span>';
    }
    item.innerHTML = `${flag}<span class="t-country-name">${esc(vote.country || '?')}</span>`;
    listEl.appendChild(item);
    const cnt = $id('cnt-' + vote.choice);
    if (cnt) {
      cnt.style.transform = 'scale(1.3)';
      setTimeout(() => { cnt.style.transform = 'scale(1)'; }, 200);
    }
  }

  function updateCounts(c) {
    const fav = $id('cnt-favor');
    const con = $id('cnt-contra');
    const abs = $id('cnt-abstencao');
    if (fav) fav.textContent = c.favor || 0;
    if (con) con.textContent = c.contra || 0;
    if (abs) abs.textContent = c.abstencao || 0;
  }

  function showResult(data) {
    clearInterval(voteInterval);
    currentSession = null;
    show('resultScreen');
    const ov = $id('oradores-overlay');
    if (ov) ov.remove();
    const c = data.counts || { favor: 0, contra: 0, abstencao: 0 };
    const max = Math.max(c.favor, c.contra, c.abstencao, 1);
    const mH = 160;
    const titleEl = $id('rTitle');
    const favEl = $id('r-favor');
    const conEl = $id('r-contra');
    const absEl = $id('r-abs');
    if (titleEl) titleEl.textContent = data.title;
    if (favEl) favEl.textContent = c.favor;
    if (conEl) conEl.textContent = c.contra;
    if (absEl) absEl.textContent = c.abstencao;
    setTimeout(() => {
      const rbFav = $id('rb-favor');
      const rbCon = $id('rb-contra');
      const rbAbs = $id('rb-abs');
      if (rbFav) rbFav.style.height = (c.favor / max * mH) + 'px';
      if (rbCon) rbCon.style.height = (c.contra / max * mH) + 'px';
      if (rbAbs) rbAbs.style.height = (c.abstencao / max * mH) + 'px';
    }, 100);
    const v = $id('rVerdict');
    if (v) {
      if (c.favor > c.contra) {
        v.textContent = '\u2705 Resolu\u00e7\u00e3o Aprovada';
        v.className = 'result-verdict v-ok';
      } else if (c.contra > c.favor) {
        v.textContent = '\u274C Resolu\u00e7\u00e3o Rejeitada';
        v.className = 'result-verdict v-no';
      } else {
        v.textContent = '\uD83E\uDD1D Empate';
        v.className = 'result-verdict v-tie';
      }
    }
    const ct = $id('committeeTag');
    if (ct) ct.style.display = 'none';
  }

  /* ---- Oradores ---- */
  function showOradores(data) {
    SCREENS.forEach((s) => {
      const e = $id(s);
      if (e) e.style.display = 'none';
    });
    const old = $id('oradores-overlay');
    if (old) old.remove();

    const overlay = document.createElement('div');
    overlay.id = 'oradores-overlay';
    overlay.style.cssText = 'position:fixed;top:110px;left:0;right:0;bottom:36px;z-index:200;background:var(--navy-d,#0B1535);overflow:auto;padding:24px 32px';

    const header = document.createElement('div');
    header.style.cssText = 'display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,.1)';
    header.innerHTML = `<div style="font-family:'DM Sans',sans-serif;font-size:13px;font-weight:700;text-transform:uppercase;letter-spacing:.16em;color:var(--gold,#C9A84C)"><span class="live-dot"></span> Lista de Oradores</div><div id="oradores-count" style="font-family:'Playfair Display',serif;font-size:28px;font-weight:900;color:var(--gold,#C9A84C)">${data.oradores ? data.oradores.length : 0}</div>`;
    overlay.appendChild(header);

    const grid = document.createElement('div');
    grid.style.cssText = 'display:flex;flex-wrap:wrap;gap:12px';
    if (data.oradores) {
      data.oradores.forEach((d) => {
        const card = document.createElement('div');
        card.style.cssText = 'display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px 20px;min-width:140px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);border-radius:8px';
        let flagHtml = '';
        if (d.flag_url && d.flag_url.trim()) {
          flagHtml = `<img src="${d.flag_url}" style="height:36px;border-radius:4px;box-shadow:0 2px 12px rgba(0,0,0,.4)" onerror="this.style.display='none'">`;
        } else if (d.flag) {
          flagHtml = `<span style="font-size:44px;line-height:1">${d.flag}</span>`;
        } else {
          flagHtml = '<span style="font-size:44px;line-height:1">\uD83C\uDF0D</span>';
        }
        card.innerHTML = flagHtml + `<span style="font-size:13px;font-weight:600;color:var(--white,#fff);text-align:center">${esc(d.country || '?')}</span>`;
        grid.appendChild(card);
      });
    }
    overlay.appendChild(grid);
    document.body.appendChild(overlay);
  }

  function hideOradores() {
    const ov = $id('oradores-overlay');
    if (ov) ov.remove();
    show('idleScreen');
  }

  /* ---- Chamada ---- */
  function renderChamadaColumn(listId, countId, items) {
    const list = $id(listId);
    const cnt = $id(countId);
    if (!list) return;
    list.innerHTML = '';
    items.forEach((d) => {
      const item = document.createElement('div');
      item.className = 'ch-country-item';
      item.dataset.id = d.id;
      let flag = '';
      if (d.flag_url && d.flag_url.trim()) {
        flag = `<img class="ch-flag-img" src="${d.flag_url}" onerror="this.style.display='none'">`;
      } else if (d.flag) {
        flag = `<span class="ch-flag-emoji">${d.flag}</span>`;
      } else {
        flag = '<span class="ch-flag-emoji">\uD83C\uDF0D</span>';
      }
      item.innerHTML = `${flag}<span class="ch-country-name">${esc(d.country || '?')}</span>`;
      list.appendChild(item);
    });
    if (cnt) cnt.textContent = items.length;
  }

  function showChamada(data) {
    show('chamadaScreen');
    const committee = data.committee || 'Geral';
    const chTitle = $id('chCommittee');
    if (chTitle) chTitle.textContent = `Chamada \u2014 ${committee.toUpperCase()}`;
    const presentes = [], votantes = [], ausentes = [];
    if (data.delegations) {
      data.delegations.forEach((d) => {
        if (d.status === 'votante') votantes.push(d);
        else if (d.status === 'presente') presentes.push(d);
        else ausentes.push(d);
      });
    }
    renderChamadaColumn('chListPresente', 'chCntPresente', presentes);
    renderChamadaColumn('chListVotante', 'chCntVotante', votantes);
    renderChamadaColumn('chListAusente', 'chCntAusente', ausentes);
    const cp = $id('chCntPresente');
    const cv = $id('chCntVotante');
    const ca = $id('chCntAusente');
    if (cp) cp.textContent = presentes.length;
    if (cv) cv.textContent = votantes.length;
    if (ca) ca.textContent = ausentes.length;
  }

  /* ---- Chamada: update individual item ---- */
  function updateChamadaItem(data) {
    const listIds = { presente: 'chListPresente', votante: 'chListVotante', ausente: 'chListAusente' };
    const countIds = { presente: 'chCntPresente', votante: 'chCntVotante', ausente: 'chCntAusente' };
    /* Remove item from all columns */
    Object.values(listIds).forEach((id) => {
      const list = $id(id);
      if (!list) return;
      const items = list.querySelectorAll('.ch-country-item');
      items.forEach((el) => {
        if (el.dataset.id === String(data.id)) el.remove();
      });
    });
    /* Add to new column */
    const targetList = $id(listIds[data.status]);
    if (targetList) {
      const item = document.createElement('div');
      item.className = 'ch-country-item';
      item.dataset.id = data.id;
      let flag = '';
      if (data.flag_url && data.flag_url.trim()) {
        flag = `<img class="ch-flag-img" src="${esc(data.flag_url)}" onerror="this.style.display='none'">`;
      } else if (data.flag) {
        flag = `<span class="ch-flag-emoji">${esc(data.flag)}</span>`;
      } else {
        flag = '<span class="ch-flag-emoji">\uD83C\uDF0D</span>';
      }
      item.innerHTML = `${flag}<span class="ch-country-name">${esc(data.country || '?')}</span>`;
      targetList.appendChild(item);
    }
    /* Update counters */
    Object.keys(countIds).forEach((key) => {
      const list = $id(listIds[key]);
      const cnt = $id(countIds[key]);
      if (list && cnt) cnt.textContent = list.querySelectorAll('.ch-country-item').length;
    });
  }

  /* ---- Speaker Queue ---- */
  let sqActiveEntry = null;

  function updateActiveSpeakerDisplay(entry) {
    const card = $id('sqActiveCard');
    if (card) card.style.display = 'flex';
    const countryEl = $id('sqActiveCountry');
    let flag = '';
    if (entry.flag_url && entry.flag_url.trim()) {
      flag = `<img src="${esc(entry.flag_url)}" style="height:40px;border-radius:4px;box-shadow:0 2px 12px rgba(0,0,0,.4)" onerror="this.style.display='none'">`;
    } else if (entry.flag) {
      flag = `<span style="font-size:40px">${esc(entry.flag)}</span>`;
    } else {
      flag = '<span style="font-size:40px">\uD83C\uDF0D</span>';
    }
    if (countryEl) countryEl.innerHTML = `${flag}<span>${esc(entry.country || '?')}</span>`;
    const topicEl = $id('sqActiveTopic');
    if (topicEl) topicEl.textContent = entry.topic || '';
  }

  function showSpeakerQueue(data) {
    show('speakerQueueScreen');
    renderSpeakerQueue(data);
  }

  function renderSpeakerQueue(data) {
    const committee = data.committee || 'all';
    const sqTitle = $id('sqCommittee');
    if (sqTitle) sqTitle.textContent = committee === 'all' ? 'Todos os Comit\u00eas' : committee.toUpperCase();

    const active = data.active;
    const queue = data.queue || [];

    if (active) {
      sqActiveEntry = active;
      updateActiveSpeakerDisplay(active);
    } else {
      sqActiveEntry = null;
      const card = $id('sqActiveCard');
      if (card) card.style.display = 'none';
    }

    const list = $id('sqList');
    const sqCnt = $id('sqCountQueue');
    if (list) list.innerHTML = '<div class="sq-list-title">Pr\u00f3ximos Oradores</div>';
    if (sqCnt) sqCnt.textContent = queue.length;

    queue.forEach((entry) => {
      const item = document.createElement('div');
      item.className = 'sq-item';
      let flag = '';
      if (entry.flag_url && entry.flag_url.trim()) {
        flag = `<img class="sq-item-flag" src="${esc(entry.flag_url)}" onerror="this.style.display='none'">`;
      } else if (entry.flag) {
        flag = `<span class="sq-item-flag-emoji">${esc(entry.flag)}</span>`;
      } else {
        flag = '<span class="sq-item-flag-emoji">\uD83C\uDF0D</span>';
      }
      item.innerHTML =
        `<span class="sq-item-pos">${entry.position}</span>` +
        flag +
        `<span class="sq-item-country">${esc(entry.country || '?')}</span>` +
        (entry.topic ? `<span class="sq-item-topic">${esc(entry.topic)}</span>` : '') +
        `<span class="sq-item-time">${entry.speaking_time}s</span>`;
      if (list) list.appendChild(item);
    });

    if (queue.length === 0 && list) {
      const empty = document.createElement('div');
      empty.style.cssText = 'text-align:center;padding:40px;color:rgba(255,255,255,.3);font-size:14px;';
      empty.textContent = 'Nenhum orador na fila';
      list.appendChild(empty);
    }
  }

  /* ---- Motion Queue ---- */
  function showMotionQueue(data) { show('motionScreen'); renderMotionQueue(data); }

  function renderMotionQueue(data) {
    const committee = data.committee || 'all';
    const moTitle = $id('moCommittee');
    if (moTitle) moTitle.textContent = committee === 'all' ? 'Todos os Comit\u00eas' : committee.toUpperCase();

    const active = data.active;
    const pending = data.pending || [];

    if (active) {
      renderMotionActive(active);
    } else {
      const card = $id('moActiveCard');
      if (card) card.style.display = 'none';
    }

    const list = $id('moList');
    const moCnt = $id('moCountPending');
    if (list) list.innerHTML = '<div class="mo-list-title">\uD83D\uDCCB Fila Pendente</div>';
    if (moCnt) moCnt.textContent = pending.length;

    pending.forEach((m) => {
      const item = document.createElement('div');
      item.className = 'mo-item';
      let proposerFlag = '';
      if (m.proposer_flag_url && m.proposer_flag_url.trim()) {
        proposerFlag = `<img src="${esc(m.proposer_flag_url)}" style="height:20px;border-radius:3px;box-shadow:0 1px 6px rgba(0,0,0,.3)" onerror="this.style.display='none'">`;
      } else if (m.proposer_flag) {
        proposerFlag = `<span style="font-size:18px">${esc(m.proposer_flag)}</span>`;
      } else {
        proposerFlag = '<span style="font-size:18px">\uD83C\uDF0D</span>';
      }
      item.innerHTML =
        `<span class="mo-item-type">${esc(m.type_icon)}</span>` +
        `<div class="mo-item-info">` +
          `<div class="mo-item-topic">${esc(m.topic)}</div>` +
          `<div class="mo-item-meta">` +
            proposerFlag +
            `<span>${esc(m.proposer_country)}</span>` +
            '<span>\u00B7</span>' +
            `<span>${m.total_time > 0 ? Math.floor(m.total_time / 60) + 'min' : 'Voto'}</span>` +
            (m.seconded_by_country ? `<span>\u00B7 Secondada por ${esc(m.seconded_by_country)}</span>` : '') +
          '</div>' +
        '</div>' +
        `<span class="mo-item-status mo-status-pending">${esc(m.type_label)}</span>`;
      if (list) list.appendChild(item);
    });

    if (pending.length === 0 && list) {
      const empty = document.createElement('div');
      empty.style.cssText = 'text-align:center;padding:40px;color:rgba(255,255,255,.3);font-size:14px;';
      empty.textContent = 'Nenhuma mo\u00e7\u00e3o pendente';
      list.appendChild(empty);
    }
  }

  function renderMotionActive(m) {
    const card = $id('moActiveCard');
    if (card) card.style.display = 'flex';
    const typeEl = $id('moActiveType');
    const topicEl = $id('moActiveTopic');
    const metaEl = $id('moActiveMeta');
    if (typeEl) typeEl.innerHTML = `\u25B6 ${esc(m.type_icon)} ${esc(m.type_label.toUpperCase())} \u2014 EM ANDAMENTO`;
    if (topicEl) topicEl.textContent = m.topic;
    if (metaEl) metaEl.textContent =
      `Proposta por: ${m.proposer_country} \u00B7 Total: ${Math.floor(m.total_time / 60)}min \u00B7 Orador: ${m.speaking_time}s`;
  }

  /* ---- Resolucoes ---- */
  function showResolutionDisplay(data) {
    if (data.active) { show('resolutionScreen'); renderResolution(data.active); }
    else if (data.submitted && data.submitted.length > 0) { show('resolutionScreen'); renderResolution(data.submitted[0]); }
  }
  function showResolutionVoting(data) { show('resolutionScreen'); renderResolution(data); }
  function showResolutionCompleted(data) { show('resolutionScreen'); renderResolutionCompleted(data); }

  function renderResolution(res) {
    const titleEl = $id('rsTitle');
    const statusEl = $id('rsStatus');
    if (titleEl) titleEl.textContent = res.title;
    if (statusEl) {
      if (res.status === 'voting') {
        statusEl.textContent = 'EM VOTA\u00C7\u00C3O';
        statusEl.className = 'rs-status rs-status-voting';
      } else {
        statusEl.textContent = 'SUBMETIDA';
        statusEl.className = 'rs-status rs-status-submitted';
      }
    }

    const proposerEl = $id('rsProposer');
    const flagImg = $id('rsProposerFlag');
    const flagEmoji = $id('rsProposerEmoji');
    const countryEl = $id('rsProposerCountry');
    if (proposerEl) proposerEl.style.display = 'flex';
    if (res.proposer_flag_url && res.proposer_flag_url.trim()) {
      if (flagImg) { flagImg.src = res.proposer_flag_url; flagImg.style.display = 'block'; }
      if (flagEmoji) flagEmoji.style.display = 'none';
    } else {
      if (flagImg) flagImg.style.display = 'none';
      if (flagEmoji) { flagEmoji.style.display = 'inline'; flagEmoji.textContent = res.proposer_flag || '\uD83C\uDF0D'; }
    }
    if (countryEl) countryEl.textContent = res.proposer_country;

    const body = $id('rsBody');
    if (!body) return;
    body.innerHTML = '';

    const preamb = (res.preambulatory || '').split('\n').filter((c) => c.trim());
    if (preamb.length > 0) {
      const secTitle = document.createElement('div');
      secTitle.className = 'rs-section-title';
      secTitle.textContent = '\uD83D\uDCCC CL\u00C1USULAS PREAMBULAT\u00D3RIAS';
      body.appendChild(secTitle);
      preamb.forEach((c) => {
        const clause = document.createElement('div');
        clause.className = 'rs-clause rs-clause-preambulatory';
        clause.textContent = c.trim();
        body.appendChild(clause);
      });
    }

    const oper = (res.operative || '').split('\n').filter((c) => c.trim());
    if (oper.length > 0) {
      const secTitle2 = document.createElement('div');
      secTitle2.className = 'rs-section-title';
      secTitle2.textContent = '\uD83D\uDCCB CL\u00C1USULAS OPERATIVAS';
      body.appendChild(secTitle2);
      oper.forEach((c, i) => {
        const clause = document.createElement('div');
        clause.className = 'rs-clause rs-clause-operative';
        clause.innerHTML = `<span class="rs-clause-num">${i + 1}.</span> ${esc(c.trim())}`;
        body.appendChild(clause);
      });
    }

    if (preamb.length === 0 && oper.length === 0) {
      const empty = document.createElement('div');
      empty.style.cssText = 'text-align:center;padding:40px;color:rgba(255,255,255,.3);';
      empty.textContent = 'Nenhuma cl\u00e1usula definida';
      body.appendChild(empty);
    }
  }

  function renderResolutionCompleted(res) {
    const titleEl = $id('rsTitle');
    const statusEl = $id('rsStatus');
    if (titleEl) titleEl.textContent = res.title;
    if (statusEl) {
      if (res.status === 'passed') {
        statusEl.textContent = '\u2713 APROVADA';
        statusEl.className = 'rs-status rs-status-voting';
      } else {
        statusEl.textContent = '\u2717 REJEITADA';
        statusEl.className = 'rs-status';
        statusEl.style.background = 'rgba(192,57,43,.15)';
        statusEl.style.color = 'var(--red-l)';
        statusEl.style.border = '1px solid rgba(192,57,43,.3)';
      }
    }
  }

  /* ---- WebSocket (optional, polling fallback) ---- */
  let socket = null;
  let wsConnected = false;
  try {
    socket = io({
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 3,
      reconnectionDelay: 3000,
      timeout: 8000,
    });
    socket.on('connect', () => { wsConnected = true; socket.emit('join_telao', {}); updateConnectionDot(true); });
    socket.on('disconnect', () => { wsConnected = false; updateConnectionDot(false); });
    socket.on('vote_opened', (data) => { loadSession(data); });
    socket.on('vote_update', (data) => { if (currentSession && data.id === currentSession.id) renderVotes(data); });
    socket.on('vote_closed', (data) => { showResult(data); });
    socket.on('oradores_show', (data) => { showOradores(data); });
    socket.on('oradores_hide', () => { hideOradores(); });
    socket.on('oradores_toggle', () => { poll(); });
    socket.on('chamada_show', (data) => { showChamada(data); });
    socket.on('chamada_hide', () => { show('idleScreen'); });
    socket.on('chamada_update', (data) => { updateChamadaItem(data); });
    socket.on('speaker_queue_show', (data) => { showSpeakerQueue(data); });
    socket.on('speaker_queue_hide', () => { show('idleScreen'); });
    socket.on('speaker_queue_display', (data) => { renderSpeakerQueue(data); });
    socket.on('speaker_started', (data) => { sqActiveEntry = data; updateActiveSpeakerDisplay(data); });
    socket.on('speaker_ended', () => { sqActiveEntry = null; });
    socket.on('speech_timer_start', (data) => { startSpeechTimer(data.duration || 90); });
    socket.on('speech_timer_stop', () => { stopSpeechTimer(); });
    socket.on('speech_timer_reset', () => {
      const sqScreen = $id('speakerQueueScreen');
      if (sqScreen && sqScreen.style.display !== 'none') {
        resetSpeechTimer();
        show('speakerQueueScreen');
      } else {
        resetSpeechTimer();
      }
    });
    socket.on('motion_queue_show', (data) => { showMotionQueue(data); });
    socket.on('motion_queue_hide', () => { show('idleScreen'); });
    socket.on('motion_queue_display', (data) => { renderMotionQueue(data); });
    socket.on('motion_activated', (data) => { renderMotionActive(data); });
    socket.on('motion_completed', () => { const c = $id('moActiveCard'); if (c) c.style.display = 'none'; });
    socket.on('resolution_display', (data) => { showResolutionDisplay(data); });
    socket.on('resolution_voting', (data) => { showResolutionVoting(data); });
    socket.on('debate_timer_sync', (data) => { syncDebateTimer(data); });
    socket.on('resolution_completed', (data) => { showResolutionCompleted(data); });
    socket.on('resolution_hide', () => { show('idleScreen'); });
  } catch (e) { socket = null; }

  /* ---- Polling (adaptive: faster when WS is down) ---- */
  async function poll() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      const res = await fetch('/api/telao/estado', { signal: controller.signal });
      clearTimeout(timeoutId);
      const data = await res.json();
      if (data.session) {
        if (!currentSession || currentSession.id !== data.session.id) {
          loadSession(data.session);
        } else {
          renderVotes(data.session);
        }
        if (data.session.remaining_sec !== undefined && data.session.remaining_sec <= 0 && currentSession) {
          showResult(currentSession);
          return;
        }
      } else if (!data.session && currentSession) {
        currentSession = null;
        show('idleScreen');
      }
      if (data.ticker && data.ticker.length) buildTicker(data.ticker);
      const ov = $id('oradores-overlay');
      if (ov) {
        if (data.oradores && data.oradores.length) {
          const cnt = $id('oradores-count');
          if (cnt) cnt.textContent = data.oradores.length;
        } else {
          ov.remove();
          show('idleScreen');
        }
      }
    } catch (e) {
      if (e.name !== 'AbortError') console.error('[TELAO] poll error', e);
    }
  }

  poll();
  function adaptivePollInterval() { return wsConnected ? 15000 : 5000; }
  function schedulePoll() { setTimeout(() => { poll(); schedulePoll(); }, adaptivePollInterval()); }
  schedulePoll();

})();
