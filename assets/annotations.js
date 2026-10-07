'use strict';
(() => {
  const KEY = 'telecom-course-annotations-v1';
  const MAX_ITEMS = 2000, MAX_QUOTE = 5000, MAX_NOTE = MAX_ITEMS * 2002;
  const labels = {underline: '下划线', wave: '波浪下划线', emphasis: '强调', comment: '注释'};
  const lineTypes = new Set(['underline', 'wave']);
  const chapters = new Map([...document.querySelectorAll('.chapter')].map(el => [el.id, el]));
  const $ = id => document.getElementById(id);
  const toolbar = $('annotation-toolbar'), editor = $('annotation-editor'), library = $('annotation-library');
  const preview = $('annotation-preview');
  let records = [], anchors = new Map(), pending = null, editing = null, returnToLibrary = false;
  let contextMode = null, previewId = null, editorSnapshot = null, returnToPreview = false;
  let contextIds = [];
  let selectionGesture = null, suppressMarkClick = false;
  let storageOK = true, selectionTimer, feedbackTimer;
  const uid = () => globalThis.crypto?.randomUUID?.() || `a-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  const prose = chapter => chapters.get(chapter).querySelector('.prose');
  const announce = (message, visible = true) => {
    $('annotation-status').textContent = message;
    if (visible) {
      clearTimeout(feedbackTimer);
      $('annotation-feedback').textContent = message; $('annotation-feedback').hidden = false;
      feedbackTimer = setTimeout(() => { $('annotation-feedback').hidden = true; }, 4500);
    } else { clearTimeout(feedbackTimer); $('annotation-feedback').hidden = true; }
  };
  const textElement = (tag, text, className) => {
    const el = document.createElement(tag); el.textContent = text;
    if (className) el.className = className;
    return el;
  };
  function validRecord(a) {
    return a && typeof a.id === 'string' && /^[A-Za-z0-9_-]{1,100}$/.test(a.id) && chapters.has(a.chapter)
      && Object.hasOwn(labels, a.type) && Number.isSafeInteger(a.start) && a.start >= 0
      && Number.isSafeInteger(a.end) && a.end > a.start && a.end - a.start === a.quote?.length
      && typeof a.quote === 'string' && a.quote.trim().length > 0 && a.quote.length <= MAX_QUOTE
      && typeof a.prefix === 'string' && a.prefix.length <= 48 && typeof a.suffix === 'string' && a.suffix.length <= 48
      && typeof a.note === 'string' && a.note.length <= MAX_NOTE && (a.type !== 'comment' || a.note.trim().length > 0)
      && typeof a.createdAt === 'string' && Number.isFinite(Date.parse(a.createdAt));
  }
  function parse(raw) {
    const data = JSON.parse(raw);
    if (data?.version !== 1 || !Array.isArray(data.annotations) || data.annotations.length > MAX_ITEMS
        || !data.annotations.every(validRecord) || new Set(data.annotations.map(a => a.id)).size !== data.annotations.length) {
      throw new Error('Invalid annotations');
    }
    return data.annotations.map(a => ({id:a.id, chapter:a.chapter, start:a.start, end:a.end, quote:a.quote,
      prefix:a.prefix, suffix:a.suffix, type:a.type, note:a.note, createdAt:a.createdAt}));
  }
  function contextMatches(text, a, start) {
    return text.slice(Math.max(0, start - a.prefix.length), start) === a.prefix
      && text.slice(start + a.quote.length, start + a.quote.length + a.suffix.length) === a.suffix;
  }
  function locate(text, a) {
    if (text.slice(a.start, a.end) === a.quote && contextMatches(text, a, a.start)) return {start:a.start, end:a.end};
    const candidates = [];
    for (let at = text.indexOf(a.quote); at !== -1; at = text.indexOf(a.quote, at + 1)) {
      candidates.push(at);
      if (candidates.length > 5000) return null;
    }
    const contextual = candidates.filter(at => contextMatches(text, a, at));
    const found = contextual.length === 1 ? contextual[0] : candidates.length === 1 ? candidates[0] : null;
    return found === null ? null : {start:found, end:found + a.quote.length};
  }
  function objectKey(a) {
    const anchor = locate(prose(a.chapter).textContent, a);
    return JSON.stringify([a.chapter, anchor?.start ?? a.start, anchor?.end ?? a.end, a.quote]);
  }
  function normalizeAnnotations(items) {
    const result = [], comments = new Map(), lines = new Map();
    for (const a of [...items].sort((a,b) => Date.parse(a.createdAt) - Date.parse(b.createdAt))) {
      if (lineTypes.has(a.type)) {
        const key = objectKey(a);
        if (lines.has(key)) result[lines.get(key)] = {...a};
        else { lines.set(key,result.length); result.push({...a}); }
        continue;
      }
      if (a.type !== 'comment') { result.push({...a}); continue; }
      const key = objectKey(a), existing = comments.get(key);
      if (!existing) {
        const copy = {...a}; comments.set(key, {record:copy, notes:new Set([a.note])}); result.push(copy);
      } else if (!existing.notes.has(a.note)) {
        existing.record.note += '\n\n' + a.note; existing.notes.add(a.note);
        if (existing.record.note.length > MAX_NOTE) throw new Error('Comment too large');
      }
    }
    return result;
  }
  function sameObject(a, snapshot) { return a.chapter === snapshot.chapter && objectKey(a) === objectKey(snapshot); }
  function objectRecords(snapshot) { return records.filter(a => sameObject(a, snapshot)); }
  function currentComment() {
    const exact = pending && objectRecords(pending).find(a => a.type === 'comment');
    return exact || (contextMode === 'existing' && records.filter(a => contextIds.includes(a.id) && a.type === 'comment')
      .sort((a,b) => a.quote.length-b.quote.length)[0]) || null;
  }
  function snapshotFor(a) {
    const anchor = anchors.get(a.id) || {start:a.start, end:a.end}, text = prose(a.chapter).textContent;
    return {chapter:a.chapter, ...anchor, quote:a.quote,
      prefix:text.slice(Math.max(0,anchor.start-48),anchor.start), suffix:text.slice(anchor.end,anchor.end+48)};
  }
  function rangeRect(snapshot) {
    const walker = document.createTreeWalker(prose(snapshot.chapter), NodeFilter.SHOW_TEXT);
    const range = document.createRange(); let node, offset = 0, started = false;
    while ((node = walker.nextNode())) {
      if (!started && offset + node.length > snapshot.start) {
        range.setStart(node, snapshot.start-offset); started = true;
      }
      if (started && offset + node.length >= snapshot.end) {
        range.setEnd(node, snapshot.end-offset); return range.getBoundingClientRect();
      }
      offset += node.length;
    }
    return chapters.get(snapshot.chapter).getBoundingClientRect();
  }
  function updateToolbar() {
    const existing = pending ? objectRecords(pending) : [];
    toolbar.querySelectorAll('[data-annotation-action]').forEach(button => {
      const active = button.dataset.annotationAction === 'comment' ? Boolean(currentComment())
        : existing.some(a => a.type === button.dataset.annotationAction);
      button.setAttribute('aria-pressed', String(active));
      button.title = button.dataset.annotationAction === 'comment' ? (active ? '编辑注释' : '添加注释')
        : `${active ? '移除' : '添加'}${labels[button.dataset.annotationAction]}`;
    });
    const ranges = $('annotation-target'); ranges.replaceChildren();
    const objects = new Map();
    if (pending) objects.set(objectKey(pending), pending);
    records.filter(a => contextIds.includes(a.id)).forEach(a => {
      if (!objects.has(objectKey(a))) objects.set(objectKey(a), a);
    });
    ranges.hidden = contextMode !== 'existing' || objects.size < 2;
    for (const a of objects.values()) {
      const label = a.quote.replace(/\s+/g,' ').trim();
      const option = textElement('option', `${[...a.quote].length} 字 · ${label.slice(0,12)}${label.length > 12 ? '…' : ''}`);
      option.value = a.id || ''; option.title = a.quote; ranges.append(option);
    }
    ranges.value = '';
  }
  function hidePreview() { preview.hidden = true; previewId = null; }
  function showPreview(a) {
    previewId = a.id; $('annotation-preview-quote').textContent = a.quote;
    $('annotation-preview-note').textContent = a.note; preview.hidden = false;
  }
  function openContext(a, rect = null, ids = [a.id]) {
    clearTimeout(selectionTimer); getSelection()?.removeAllRanges();
    contextMode = 'existing'; pending = snapshotFor(a); contextIds = ids.filter(Boolean);
    const comment = currentComment();
    if (comment) showPreview(comment); else hidePreview();
    updateToolbar(); toolbar.hidden = false;
    positionToolbar(rect || rangeRect(pending));
  }
  function unwrap(root) {
    root.querySelectorAll('.annotation-mark').forEach(el => el.replaceWith(...el.childNodes));
    root.normalize();
  }
  function renderChapter(chapter) {
    const root = prose(chapter); unwrap(root);
    const text = root.textContent;
    const active = records.filter(a => a.chapter === chapter).flatMap(a => {
      const anchor = locate(text, a); anchors.set(a.id, anchor);
      return anchor ? [{...a, ...anchor}] : [];
    });
    if (!active.length) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const nodes = []; let node, offset = 0;
    while ((node = walker.nextNode())) {
      nodes.push({node, start:offset, end:offset + node.length}); offset += node.length;
    }
    for (const item of nodes) {
      const hits = active.filter(a => a.start < item.end && a.end > item.start);
      if (!hits.length) continue;
      const boundaries = [...new Set([0, item.node.length, ...hits.flatMap(a => [
        Math.max(0, a.start - item.start), Math.min(item.node.length, a.end - item.start)])])].sort((a,b) => a-b);
      const fragment = document.createDocumentFragment();
      for (let i = 0; i < boundaries.length - 1; i++) {
        const left = boundaries[i], right = boundaries[i+1];
        const covering = hits.filter(a => a.start < item.start + right && a.end > item.start + left);
        const value = item.node.data.slice(left, right);
        if (covering.length) {
          const span = textElement('span', value, 'annotation-mark');
          span.dataset.annotationIds = covering.map(a => a.id).join(' ');
          covering.forEach(a => span.classList.add(`annotation-${a.type}`));
          span.title = covering.map(a => a.type === 'comment' ? a.note : labels[a.type]).join('\n');
          fragment.append(span);
        } else fragment.append(document.createTextNode(value));
      }
      item.node.replaceWith(fragment);
    }
  }
  function updatePrintNotes() {
    const root = $('annotation-print-notes'); root.replaceChildren();
    const notes = records.filter(a => a.type === 'comment');
    if (!notes.length) return;
    root.append(textElement('h2', '个人注释'));
    notes.forEach(a => {
      const article = document.createElement('article');
      article.append(textElement('h3', chapterTitle(a.chapter)), textElement('blockquote', a.quote), textElement('p', a.note));
      root.append(article);
    });
  }
  function chapterTitle(id) { return `${chapters.get(id).dataset.number} · ${chapters.get(id).querySelector('h2').textContent}`; }
  function updateState(message) {
    $('annotation-count').textContent = records.length;
    updatePrintNotes();
    announce(message || (storageOK ? `${records.length} 条标注 · 已保存到当前浏览器` : '本次标注尚未保存，请从“我的标注”导出保留'), !storageOK);
  }
  function save(changedChapters, message) {
    try { localStorage.setItem(KEY, JSON.stringify({version:1, annotations:records})); storageOK = true; }
    catch { storageOK = false; }
    changedChapters.forEach(renderChapter);
    updateState(storageOK ? message : undefined);
  }
  function hideToolbar(clear = false) {
    toolbar.hidden = true;
    if (clear) dismissContext(true);
  }
  function dismissContext(clearSelection = false) {
    toolbar.hidden = true; pending = null; contextMode = null; contextIds = []; hidePreview();
    if (clearSelection) getSelection()?.removeAllRanges();
  }
  function positionToolbar(rect) {
    if (innerWidth <= 760) {
      toolbar.style.left = '12px'; toolbar.style.top = '';
      toolbar.style.bottom = preview.hidden ? '' : `${innerHeight - preview.getBoundingClientRect().top + 8}px`;
      return;
    }
    toolbar.style.bottom = '';
    const box = toolbar.getBoundingClientRect();
    const availableBottom = preview.hidden ? innerHeight : preview.getBoundingClientRect().top - 8;
    toolbar.style.left = `${Math.max(12, Math.min(innerWidth - box.width - 12, rect.left + rect.width / 2 - box.width / 2))}px`;
    toolbar.style.top = `${Math.max(12, Math.min(availableBottom - box.height - 12, rect.top > box.height + 16 ? rect.top - box.height - 8 : rect.bottom + 8))}px`;
  }
  function inspectSelection() {
    if (selectionGesture || editor.open || library.open || toolbar.contains(document.activeElement)) return;
    const selection = getSelection();
    if (!selection || selection.isCollapsed || !selection.rangeCount) {
      if (contextMode !== 'existing') dismissContext();
      return;
    }
    const range = selection.getRangeAt(0);
    if (preview.contains(range.commonAncestorContainer)) return;
    const parent = node => (node.nodeType === Node.ELEMENT_NODE ? node : node.parentElement)?.closest('.prose');
    const root = parent(range.startContainer), endRoot = parent(range.endContainer);
    if (!root || !endRoot) { dismissContext(); return; }
    if (root !== endRoot) { dismissContext(); announce('请在同一章节的正文中选择文字'); return; }
    const prefixRange = document.createRange(); prefixRange.selectNodeContents(root); prefixRange.setEnd(range.startContainer, range.startOffset);
    const start = prefixRange.toString().length, quote = range.toString(), end = start + quote.length;
    if (!quote.trim()) { dismissContext(); return; }
    if (quote.length > MAX_QUOTE) { dismissContext(); announce('一次可标注最多 5000 个字符，请缩短选区'); return; }
    const text = root.textContent;
    pending = {chapter:root.closest('.chapter').id, start, end, quote, prefix:text.slice(Math.max(0,start-48), start), suffix:text.slice(end,end+48)};
    contextMode = 'selection'; contextIds = [];
    const comment = objectRecords(pending).find(a => a.type === 'comment');
    if (comment) showPreview(comment); else hidePreview();
    updateToolbar();
    toolbar.hidden = false; positionToolbar(range.getBoundingClientRect());
  }
  function scheduleSelection() { clearTimeout(selectionTimer); selectionTimer = setTimeout(inspectSelection, 100); }
  document.addEventListener('selectionchange', scheduleSelection);
  document.addEventListener('pointerup', event => {
    if (selectionGesture && event.pointerId === selectionGesture.id) {
      suppressMarkClick = selectionGesture.moved || !getSelection()?.isCollapsed;
      selectionGesture = null;
    }
    scheduleSelection();
  });
  document.addEventListener('pointercancel', event => {
    if (selectionGesture?.id !== event.pointerId) return;
    selectionGesture = null; suppressMarkClick = true; scheduleSelection();
  });
  document.addEventListener('pointermove', event => {
    if (selectionGesture?.id === event.pointerId
        && Math.hypot(event.clientX-selectionGesture.x,event.clientY-selectionGesture.y) >= 4) selectionGesture.moved = true;
  }, {passive:true});
  window.addEventListener('blur', () => { selectionGesture = null; scheduleSelection(); });
  document.addEventListener('keyup', event => { if (event.key !== 'Escape') scheduleSelection(); });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !editor.open && !library.open) hideToolbar(true);
    if (event.key === 'Tab' && !event.shiftKey && !toolbar.hidden && !editor.open && !library.open
        && !toolbar.contains(document.activeElement) && !preview.contains(document.activeElement)
        && !document.activeElement.matches('button,input,textarea,select,a[href]')) {
      event.preventDefault(); toolbar.querySelector('button').focus();
    }
  });
  document.addEventListener('pointerdown', event => {
    if (event.isPrimary === false || event.button !== 0) return;
    suppressMarkClick = false;
    if (editor.open || library.open || event.target.closest('#annotation-toolbar,#annotation-preview')) return;
    if (event.target.closest('.prose')) {
      selectionGesture = {id:event.pointerId, x:event.clientX, y:event.clientY, moved:false};
      clearTimeout(selectionTimer);
    }
    dismissContext();
  });
  window.addEventListener('scroll', () => {
    if (selectionGesture || toolbar.hidden || innerWidth <= 760) return;
    if (contextMode !== 'existing') { dismissContext(); return; }
    const a = objectRecords(pending)[0];
    const mark = a && [...prose(a.chapter).querySelectorAll('.annotation-mark')].find(el => el.dataset.annotationIds.split(' ').includes(a.id));
    if (mark) positionToolbar(mark.getBoundingClientRect());
  }, {passive:true});
  window.addEventListener('resize', () => {
    if (toolbar.hidden) return;
    if (contextMode === 'existing') {
      const a = objectRecords(pending)[0]; if (a) openContext(a, null, contextIds);
    } else inspectSelection();
  });
  toolbar.addEventListener('pointerdown', event => { if (event.target.closest('button')) event.preventDefault(); });
  $('close-annotation-toolbar').addEventListener('click', () => hideToolbar(true));
  function openEditor(snapshot, record = null, fromLibrary = false) {
    record ||= objectRecords(snapshot).find(a => a.type === 'comment') || currentComment();
    editing = record?.id || null; editorSnapshot = record ? snapshotFor(record) : {...snapshot}; returnToLibrary = fromLibrary;
    returnToPreview = !fromLibrary;
    hideToolbar(true);
    $('annotation-editor-title').textContent = record ? '编辑注释' : '添加注释';
    $('annotation-quote').textContent = editorSnapshot.quote;
    $('annotation-note').maxLength = Math.max(2000, record?.note.length || 0);
    $('annotation-note').value = record?.note || ''; $('annotation-editor-error').textContent = '';
    if (library.open) library.close();
    editor.showModal(); $('annotation-note').focus();
  }
  function add(type, snapshot, note = '') {
    const existing = objectRecords(snapshot).find(a => a.type === type);
    if (existing) {
      if (type === 'comment') { existing.note = note; save(new Set([existing.chapter])); }
      return true;
    }
    if (records.length >= MAX_ITEMS) { announce('标注已达到 2000 条，请先导出并整理现有标注'); return false; }
    records.push({...snapshot, id:uid(), type, note, createdAt:new Date().toISOString()});
    save(new Set([snapshot.chapter])); return true;
  }
  toolbar.addEventListener('click', event => {
    const button = event.target.closest('[data-annotation-action]');
    if (!button || !pending) return;
    const snapshot = {...pending}, type = button.dataset.annotationAction;
    if (type === 'comment') openEditor(snapshot);
    else {
      const existing = objectRecords(snapshot).filter(a => a.type === type), keepOpen = contextMode === 'existing';
      if (existing.length) {
        const ids = new Set(existing.map(a => a.id)); records = records.filter(a => !ids.has(a.id));
        existing.forEach(a => anchors.delete(a.id)); save(new Set([snapshot.chapter]));
      } else {
        if (lineTypes.has(type)) {
          const replaced = objectRecords(snapshot).filter(a => lineTypes.has(a.type));
          const ids = new Set(replaced.map(a => a.id)); records = records.filter(a => !ids.has(a.id));
          replaced.forEach(a => anchors.delete(a.id));
        }
        add(type, snapshot);
      }
      if (keepOpen) {
        const remaining = objectRecords(snapshot)[0];
        openContext(remaining || snapshot, null, [...contextIds, ...objectRecords(snapshot).map(a => a.id)]);
      } else hideToolbar(true);
    }
  });
  function closeEditor() { editor.close(); }
  editor.querySelectorAll('[data-close-editor]').forEach(button => button.addEventListener('click', closeEditor));
  editor.addEventListener('close', () => {
    const snapshot = editorSnapshot;
    editorSnapshot = null; editing = null;
    if (returnToLibrary) { returnToLibrary = false; openLibrary(); }
    else if (returnToPreview && snapshot) {
      const a = objectRecords(snapshot).find(item => item.type === 'comment');
      if (a) openContext(a);
    }
    returnToPreview = false;
  });
  $('annotation-form').addEventListener('submit', event => {
    event.preventDefault(); const note = $('annotation-note').value.trim();
    if (!note) { $('annotation-editor-error').textContent = '请输入注释内容'; $('annotation-note').focus(); return; }
    if (editing) {
      const record = records.find(a => a.id === editing); record.note = note; save(new Set([record.chapter]));
    } else if (!add('comment', editorSnapshot, note)) { $('annotation-editor-error').textContent = '标注已达到 2000 条，请先整理现有标注'; return; }
    editor.close();
  });
  function actionButton(text, callback) {
    const button = textElement('button', text); button.type = 'button'; button.addEventListener('click', callback); return button;
  }
  function jump(a) {
    library.close(); hideToolbar(true);
    const search = $('search');
    if (search.value) { search.value = ''; search.dispatchEvent(new Event('input')); }
    const root = prose(a.chapter);
    root.querySelectorAll('.annotation-mark').forEach(el => {
      if (el.dataset.annotationIds.split(' ').includes(a.id)) {
        for (let parent = el.parentElement; parent && parent !== root; parent = parent.parentElement) if (parent.tagName === 'DETAILS') parent.open = true;
      }
    });
    const target = [...root.querySelectorAll('.annotation-mark')].find(el => el.dataset.annotationIds.split(' ').includes(a.id)) || chapters.get(a.chapter);
    location.hash = a.chapter; target.scrollIntoView({block:'center', behavior:'auto'});
    target.classList.add('annotation-located'); setTimeout(() => target.classList.remove('annotation-located'), 2000);
    chapters.get(a.chapter).querySelector('h2').setAttribute('tabindex', '-1');
    chapters.get(a.chapter).querySelector('h2').focus({preventScroll:true});
  }
  function renderList() {
    const list = $('annotation-list'); list.replaceChildren();
    const items = records;
    if (!items.length) { list.append(textElement('p', '选中正文即可添加下划线、强调或注释。', 'annotation-empty')); return; }
    const sorted = [...items].sort((a,b) => a.chapter.localeCompare(b.chapter) || (anchors.get(a.id)?.start ?? a.start) - (anchors.get(b.id)?.start ?? b.start));
    sorted.forEach(a => {
      const card = document.createElement('article'); card.className = 'annotation-card'; card.dataset.recordId = a.id;
      card.append(textElement('p', `${chapterTitle(a.chapter)} · ${labels[a.type]}`, 'annotation-card-meta'), textElement('blockquote', a.quote));
      if (a.note) card.append(textElement('p', a.note, 'annotation-card-note'));
      if (!anchors.get(a.id)) card.append(textElement('p', '原文位置待确认，摘录与注释已保留。', 'annotation-unresolved'));
      const actions = document.createElement('div'); actions.className = 'annotation-card-actions';
      actions.append(actionButton(anchors.get(a.id) ? '回到原文' : '查看章节', () => jump(a)));
      if (a.type === 'comment') actions.append(actionButton('编辑注释', () => openEditor(a, a, true)));
      actions.append(actionButton('删除', () => {
        records = records.filter(item => item.id !== a.id); anchors.delete(a.id); save(new Set([a.chapter]));
        renderList(); $('annotation-library-status').textContent = storageOK ? `已删除${labels[a.type]}`
          : `已从本页删除${labels[a.type]}，修改尚未保存，请点击“导出标注”保留`;
        // Keep keyboard focus on the next available action after the removed card disappears.
        (list.querySelector('button') || $('close-annotation-library')).focus();
      }));
      card.append(actions); list.append(card);
    });
  }
  function openLibrary() {
    hideToolbar(true); $('annotation-library-status').textContent = storageOK ? '' : '本次标注尚未保存，请点击“导出标注”保留';
    renderList(); library.showModal();
  }
  $('open-annotations').addEventListener('click', () => openLibrary());
  $('close-annotation-library').addEventListener('click', () => library.close());
  document.addEventListener('click', event => {
    const mark = event.target.closest('.annotation-mark');
    if (!mark || suppressMarkClick || selectionGesture || !getSelection()?.isCollapsed || event.target.closest('a')) return;
    const items = mark.dataset.annotationIds.split(' ').map(id => records.find(a => a.id === id)).filter(Boolean);
    items.sort((a,b) => a.quote.length-b.quote.length || a.id.localeCompare(b.id));
    if (items[0]) openContext(items[0], mark.getBoundingClientRect(), items.map(a => a.id));
  });
  $('annotation-target').addEventListener('change', event => {
    const a = records.find(item => item.id === event.target.value);
    if (a) openContext(a, null, contextIds);
  });
  $('close-annotation-preview').addEventListener('click', () => {
    hidePreview();
    if (!toolbar.hidden && pending) {
      const a = objectRecords(pending)[0];
      const mark = a && [...prose(a.chapter).querySelectorAll('.annotation-mark')].find(el => el.dataset.annotationIds.split(' ').includes(a.id));
      positionToolbar(mark?.getBoundingClientRect() || toolbar.getBoundingClientRect());
    }
  });
  $('edit-annotation-preview').addEventListener('click', () => {
    const a = records.find(item => item.id === previewId); if (a) openEditor(snapshotFor(a), a);
  });
  $('delete-annotation-preview').addEventListener('click', () => {
    const a = records.find(item => item.id === previewId); if (!a) return;
    const snapshot = snapshotFor(a);
    records = records.filter(item => item.id !== a.id); anchors.delete(a.id); save(new Set([a.chapter]));
    const remaining = objectRecords(snapshot)[0];
    if (remaining) openContext(remaining, null, contextIds); else hideToolbar(true);
    announce(storageOK ? '已删除注释' : '已从本页删除注释，修改尚未保存，请从“我的标注”导出保留');
  });
  $('export-annotations').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify({version:1, annotations:records}, null, 2)], {type:'application/json'});
    const url = URL.createObjectURL(blob), link = document.createElement('a');
    link.href = url; link.download = `网络运维教程-标注-${new Date().toISOString().slice(0,10)}.json`;
    link.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    $('annotation-library-status').textContent = `已导出 ${records.length} 条标注`;
  });
  $('import-annotations').addEventListener('click', () => $('annotation-file').click());
  const identity = a => JSON.stringify([a.chapter,a.start,a.end,a.quote,a.prefix,a.suffix,a.type]);
  const signature = a => JSON.stringify([identity(a),a.note]);
  $('annotation-file').addEventListener('change', async event => {
    const file = event.target.files[0]; if (!file) return;
    try {
      if (file.size > 20 * 1024 * 1024) throw new Error('Too large');
      const incoming = normalizeAnnotations(parse(await file.text())), merged = [...records], ids = new Map(records.map(a => [a.id, a]));
      const signatures = new Set(records.map(signature));
      for (const a of incoming) {
        if (a.type === 'comment' && records.some(item => item.type === 'comment' && sameObject(item,a))) continue;
        if (lineTypes.has(a.type) && records.some(item => lineTypes.has(item.type) && sameObject(item,a))) continue;
        if (signatures.has(signature(a)) || (ids.has(a.id) && identity(ids.get(a.id)) === identity(a))) continue;
        if (ids.has(a.id)) a.id = uid();
        merged.push(a); ids.set(a.id, a); signatures.add(signature(a));
      }
      const normalized = normalizeAnnotations(merged);
      if (normalized.length > MAX_ITEMS) throw new Error('Too many annotations');
      const currentIds = new Set(records.map(a => a.id)), count = normalized.filter(a => !currentIds.has(a.id)).length;
      records = normalized; save(new Set(incoming.map(a => a.chapter))); renderList();
      $('annotation-library-title').textContent = '我的标注';
      $('annotation-library-status').textContent = `已导入 ${count} 条新标注，现有标注已保留${storageOK ? '' : '；本次未保存，请导出保留'}`;
    } catch { $('annotation-library-status').textContent = '无法读取这个标注文件，请选择本教程导出的 JSON 文件'; }
    event.target.value = '';
  });
  try {
    const raw = localStorage.getItem(KEY);
    if (raw) {
      const original = parse(raw); records = normalizeAnnotations(original);
      if (records.length !== original.length) localStorage.setItem(KEY, JSON.stringify({version:1, annotations:records}));
    }
  }
  catch { storageOK = false; }
  new Set(records.map(a => a.chapter)).forEach(renderChapter);
  updateState(records.length ? undefined : storageOK ? '标注保存在当前浏览器，可导出备份' : '标注保存暂不可用，可在阅读后导出保留');
})();
