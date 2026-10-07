'use strict';
(() => {
  const chapters = [...document.querySelectorAll('.chapter')];
  const links = [...document.querySelectorAll('.toc-link')];
  const buttons = [...document.querySelectorAll('[data-complete]')];
  const search = document.getElementById('search');
  const status = document.getElementById('search-status');
  const menu = document.querySelector('.course-menu');
  const searchIndex = new Map(chapters.map(c => [c.id, c.querySelector('.prose').textContent.toLocaleLowerCase() + ' ' + c.querySelector('h2').textContent.toLocaleLowerCase()]));
  const validIds = new Set(chapters.map(c => c.id));
  const key = 'telecom-course-progress-v1';
  let done = new Set();
  let storageWorks = true;
  function readStorage(name) { try { return localStorage.getItem(name); } catch { storageWorks = false; return null; } }
  function writeStorage(name, value) { try { localStorage.setItem(name, value); } catch { storageWorks = false; } updateStorageNote(); }
  function updateStorageNote() { document.getElementById('storage-note').textContent = storageWorks ? '进度保存在当前浏览器' : '当前浏览器未保存进度，本次阅读仍可标记'; }
  try { const value = JSON.parse(readStorage(key) || '[]'); if (Array.isArray(value)) done = new Set(value.filter(id => validIds.has(id))); } catch { done = new Set(); }
  function renderProgress() {
    document.getElementById('progress').value = done.size;
    document.getElementById('progress-label').textContent = `${done.size} / ${chapters.length}`;
    buttons.forEach(b => { const completed = done.has(b.dataset.complete); b.setAttribute('aria-pressed', String(completed)); b.textContent = completed ? '✓ 已学完 · 点击取消' : '标记本章已学完'; });
    links.forEach(a => a.classList.toggle('done', done.has(a.dataset.chapter)));
  }
  buttons.forEach(b => b.addEventListener('click', () => { const id = b.dataset.complete; if (done.has(id)) done.delete(id); else done.add(id); writeStorage(key, JSON.stringify([...done])); renderProgress(); }));
  document.getElementById('reset-progress').addEventListener('click', () => { done.clear(); writeStorage(key, '[]'); renderProgress(); });
  function filterChapters() {
    const term = search.value.trim().toLocaleLowerCase();
    let matches = 0;
    chapters.forEach(c => { c.hidden = Boolean(term) && !searchIndex.get(c.id).includes(term); if (!c.hidden) matches++; });
    links.forEach(a => { a.hidden = document.getElementById(a.dataset.chapter).hidden; });
    document.querySelectorAll('.toc-group').forEach(g => { g.hidden = ![...g.querySelectorAll('.toc-link')].some(a => !a.hidden); });
    document.getElementById('no-results').hidden = matches > 0;
    document.getElementById('clear-search').hidden = !search.value;
    document.querySelector('.path-cards').hidden = Boolean(term);
    status.textContent = term ? `“${search.value.trim()}” 匹配 ${matches} 个章节` : `${chapters.length} 个章节 · 可离线阅读`;
    markActive();
  }
  function clearSearch() { search.value = ''; filterChapters(); }
  search.addEventListener('input', filterChapters);
  search.addEventListener('keydown', e => { if (e.key === 'Escape') clearSearch(); });
  document.getElementById('clear-search').addEventListener('click', () => { clearSearch(); search.focus(); });
  document.getElementById('restore').addEventListener('click', () => { clearSearch(); search.focus(); });
  let current = '';
  function markActive() {
    const visible = chapters.filter(c => !c.hidden);
    const reference = window.innerHeight * 0.24;
    const above = visible.filter(c => c.getBoundingClientRect().top <= reference);
    const active = above.length ? above[above.length - 1] : visible[0];
    const id = active ? active.id : '';
    if (current === id) return;
    current = id;
    links.forEach(a => { const isActive = a.dataset.chapter === id; a.classList.toggle('active', isActive); if (isActive) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current'); });
  }
  let queued = false;
  window.addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(() => { queued = false; markActive(); }); } }, { passive: true });
  document.addEventListener('click', e => {
    const a = e.target.closest('a[href^="#chapter-"]');
    if (!a) return;
    const target = document.getElementById(a.getAttribute('href').slice(1));
    if (!target) return;
    if (target.hidden) clearSearch();
    if (window.matchMedia('(max-width: 760px)').matches) menu.open = false;
  });
  const fontSelect = document.getElementById('font-size');
  const fonts = { standard: '', large: '19px', larger: '21px' };
  const savedFont = readStorage('telecom-course-font-v1');
  if (Object.hasOwn(fonts, savedFont)) fontSelect.value = savedFont;
  function applyFont() { const size = fonts[fontSelect.value]; if (size) document.body.style.setProperty('--font-size', size); else document.body.style.removeProperty('--font-size'); }
  fontSelect.addEventListener('change', () => { applyFont(); writeStorage('telecom-course-font-v1', fontSelect.value); });
  let previouslyClosed = [];
  window.addEventListener('beforeprint', () => { previouslyClosed = [...document.querySelectorAll('.prose details:not([open])')]; previouslyClosed.forEach(d => { d.open = true; }); });
  window.addEventListener('afterprint', () => { previouslyClosed.forEach(d => { d.open = false; }); previouslyClosed = []; });
  document.getElementById('print').addEventListener('click', () => window.print());
  if (window.matchMedia('(max-width: 760px)').matches) menu.open = false;
  renderProgress(); applyFont(); updateStorageNote(); markActive();
})();
