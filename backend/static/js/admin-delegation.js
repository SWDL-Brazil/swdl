/**
 * admin-delegation.js
 * Shared JS for delegation forms: flag search + member picker.
 *
 * Expected DOM elements (all optional — code skips missing):
 *   #searchFlag, #countryInput, #flagPreview, #flagImg, #flagName,
 *   #flagUrl, #flagEmojiManual, #flagError
 *   #membersInput, #memberSelect, #addMemberBtn, #membersPreview
 */
(function () {
  'use strict';

  /* ── FLAG SEARCH ─────────────────────────────────────────── */
  const searchBtn      = document.getElementById('searchFlag');
  const countryInput   = document.getElementById('countryInput');
  const flagPreview    = document.getElementById('flagPreview');
  const flagImg        = document.getElementById('flagImg');
  const flagName       = document.getElementById('flagName');
  const flagUrl        = document.getElementById('flagUrl');
  const flagEmojiManual= document.getElementById('flagEmojiManual');
  const flagError      = document.getElementById('flagError');

  async function searchFlag() {
    const country = countryInput.value.trim();
    if (!country) return;

    searchBtn.textContent = '⏳';
    searchBtn.disabled    = true;
    flagError.style.display    = 'none';
    flagPreview.style.display  = 'none';

    try {
      const res  = await fetch(`/api/bandeira?country=${encodeURIComponent(country)}`);
      const data = await res.json();

      if (data.ok) {
        flagImg.src          = data.flag_url;
        flagName.textContent = data.name;
        flagUrl.value        = data.flag_url;
        flagPreview.style.display = 'block';
        countryInput.value   = data.name;
        if (flagEmojiManual && !flagEmojiManual.value) flagEmojiManual.value = '🏳️';
      } else {
        flagError.style.display = 'block';
      }
    } catch (e) {
      flagError.style.display = 'block';
    }

    searchBtn.textContent = '🔍 Buscar';
    searchBtn.disabled    = false;
  }

  if (searchBtn) {
    searchBtn.addEventListener('click', searchFlag);
  }
  if (countryInput) {
    countryInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') { e.preventDefault(); searchFlag(); }
    });
  }

  /* ── MEMBER PICKER ───────────────────────────────────────── */
  const memberInput  = document.getElementById('membersInput');
  const memberSelect = document.getElementById('memberSelect');
  const addMemberBtn = document.getElementById('addMemberBtn');
  const membersPrev  = document.getElementById('membersPreview');

  if (!memberInput || !memberSelect || !addMemberBtn) return;

  function currentMembers() {
    return memberInput.value.split(',').map(s => s.trim()).filter(Boolean);
  }

  function renderMembersPreview() {
    if (!membersPrev) return;
    membersPrev.innerHTML = '';
    currentMembers().forEach(name => {
      const chip = document.createElement('span');
      chip.textContent = name;
      chip.style.cssText = 'display:inline-block;background:rgba(16,30,76,.06);border:1px solid var(--border);border-radius:12px;padding:2px 10px;margin:3px 4px 0 0;font-size:12px;color:var(--navy)';
      membersPrev.appendChild(chip);
    });
  }

  function findMemberOption(name) {
    return Array.from(memberSelect.options).find(o => o.value === name);
  }

  addMemberBtn.addEventListener('click', () => {
    const opt = memberSelect.options[memberSelect.selectedIndex];
    if (!opt || !opt.value || opt.disabled) return;
    const name = opt.value.trim();
    if (!name) return;
    const list = currentMembers();
    if (!list.includes(name)) {
      list.push(name);
      memberInput.value = list.join(', ');
    }
    const opt = findMemberOption(name);
    if (opt) opt.remove();
    renderMembersPreview();
  });

  memberInput.addEventListener('input', renderMembersPreview);
  renderMembersPreview();

  /* ── Expose helpers for templates that need extra logic ──── */
  window.DelegationForm = {
    currentMembers,
    findMemberOption,
    renderMembersPreview,
    memberInput,
    memberSelect,
  };
})();
