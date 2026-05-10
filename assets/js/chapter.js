// ============================================================
// chapter.js — per-beat page logic
// Loads BRANCHES (injected as inline <script> before this file).
// Handles: persistence, split-flap rewrite, decision cards,
// commit/return flow, deep-link auto-activation, multi-section fix.
// ============================================================

(function () {
  'use strict';

  const STORAGE_KEY = 'forest-state-v1';
  const BOOKMARK_KEY = 'forest-bookmark';
  const BEAT_ID = (window.__FOREST_BEAT_ID__ || '');           // e.g. "b3"
  const DEEP_LINK_BRANCH = (window.__FOREST_DEEP_LINK__ || ''); // e.g. "b3-noriko" or ""
  const REDUCED_MOTION = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ----------------------------------------------------------
  // State / persistence
  // ----------------------------------------------------------

  function readStore() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) return JSON.parse(raw);
    } catch (e) {}
    return { activeByBeat: {} };
  }
  function writeStore(s) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(s)); } catch (e) {}
  }
  function getActiveBranch() {
    const s = readStore();
    return (s.activeByBeat && s.activeByBeat[BEAT_ID]) || null;
  }
  function setActiveBranch(branchId) {
    const s = readStore();
    s.activeByBeat = s.activeByBeat || {};
    if (branchId) s.activeByBeat[BEAT_ID] = branchId;
    else delete s.activeByBeat[BEAT_ID];
    writeStore(s);
  }

  // ----------------------------------------------------------
  // Canon snapshot
  // ----------------------------------------------------------

  const canonSnapshot = {};

  function captureCanon() {
    document.querySelectorAll('.post-fork').forEach(el => {
      const id = el.dataset.forkTarget;
      canonSnapshot[id] = el.innerHTML;
    });
    document.querySelectorAll('section.section').forEach(s => {
      canonSnapshot['__' + s.id] = s.innerHTML;
    });
  }

  // ----------------------------------------------------------
  // Split-flap animation
  // ----------------------------------------------------------

  const FLAP_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,;:—';
  const TICK_MS = 50;
  const MIN_FLIPS = 5;
  const MAX_FLIPS = 22;
  const PARAGRAPH_OVERLAP = 0.55;

  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
  function randomFlapChar() { return FLAP_CHARS[Math.floor(Math.random() * FLAP_CHARS.length)]; }
  function htmlToPlainText(html) { const t = document.createElement('div'); t.innerHTML = html; return t.textContent || ''; }
  function normalizeHTML(html) { const t = document.createElement('div'); t.innerHTML = html; return t.innerHTML.trim().replace(/\s+/g, ' '); }

  function flapParagraph(pElement, targetHTML, onNearDone) {
    return new Promise(resolve => {
      // Reduced-motion: snap, no animation.
      if (REDUCED_MOTION) {
        pElement.innerHTML = targetHTML;
        if (onNearDone) onNearDone();
        resolve();
        return;
      }

      const targetText = htmlToPlainText(targetHTML);
      const oldText = pElement.textContent || '';
      const len = Math.max(oldText.length, targetText.length);
      if (len === 0) { pElement.innerHTML = targetHTML; resolve(); return; }
      const oldPadded = oldText.padEnd(len, ' ');
      const newPadded = targetText.padEnd(len, ' ');
      pElement.classList.add('flapping');
      pElement.innerHTML = '';
      const spans = [], flipsLeft = [];
      for (let i = 0; i < len; i++) {
        const span = document.createElement('span');
        span.className = 'flap-ch';
        const tgt = newPadded[i];
        span.dataset.target = tgt;
        const initChar = oldPadded[i] === ' ' && tgt !== ' ' ? randomFlapChar() : oldPadded[i];
        span.textContent = initChar === ' ' ? ' ' : initChar;
        pElement.appendChild(span);
        spans.push(span);
        flipsLeft.push(MIN_FLIPS + Math.floor(Math.random() * (MAX_FLIPS - MIN_FLIPS)));
      }
      const startTime = performance.now();
      const expectedDuration = MAX_FLIPS * TICK_MS;
      let nearDoneFired = false;
      const interval = setInterval(() => {
        let allDone = true;
        for (let i = 0; i < spans.length; i++) {
          if (flipsLeft[i] > 0) { spans[i].textContent = randomFlapChar(); flipsLeft[i]--; allDone = false; }
          else if (!spans[i].classList.contains('settled')) {
            const t = spans[i].dataset.target;
            spans[i].textContent = t === ' ' ? ' ' : t;
            spans[i].classList.add('settled');
          }
        }
        const elapsed = performance.now() - startTime;
        if (!nearDoneFired && elapsed >= expectedDuration * PARAGRAPH_OVERLAP) {
          nearDoneFired = true; if (onNearDone) onNearDone();
        }
        if (allDone) {
          clearInterval(interval);
          setTimeout(() => {
            pElement.innerHTML = targetHTML;
            pElement.classList.remove('flapping');
            if (!nearDoneFired && onNearDone) { nearDoneFired = true; onNearDone(); }
            resolve();
          }, 180);
        }
      }, TICK_MS);
    });
  }

  async function rewriteContainerParagraphs(container, newParagraphs) {
    const oldParas = Array.from(container.querySelectorAll(':scope > p'));
    const targetCount = newParagraphs.length;
    while (oldParas.length < targetCount) {
      const p = document.createElement('p'); p.textContent = ''; container.appendChild(p); oldParas.push(p);
    }
    const flapsNeeded = oldParas.map((pEl, i) => {
      const targetHTML = (i < targetCount) ? newParagraphs[i] : '';
      return normalizeHTML(pEl.innerHTML) !== normalizeHTML(targetHTML);
    });
    if (!flapsNeeded.some(x => x)) return;
    const flapPromises = [];
    let nextStartPromise = Promise.resolve();
    for (let i = 0; i < oldParas.length; i++) {
      if (!flapsNeeded[i]) continue;
      const pEl = oldParas[i];
      const targetHTML = (i < targetCount) ? newParagraphs[i] : '';
      const myStart = nextStartPromise;
      let resolveUnlock;
      nextStartPromise = new Promise(r => { resolveUnlock = r; });
      const p = (async () => {
        await myStart;
        if (targetHTML === '') { await flapParagraph(pEl, '', resolveUnlock); pEl.remove(); }
        else { await flapParagraph(pEl, targetHTML, resolveUnlock); }
      })();
      flapPromises.push(p);
    }
    await Promise.all(flapPromises);
  }

  function hasAnyChange(container, newParagraphs) {
    const oldParas = Array.from(container.querySelectorAll(':scope > p'));
    if (oldParas.length !== newParagraphs.length) return true;
    for (let i = 0; i < oldParas.length; i++) {
      if (normalizeHTML(oldParas[i].innerHTML) !== normalizeHTML(newParagraphs[i])) return true;
    }
    return false;
  }

  function findFirstChangedParagraph(container, newParagraphs) {
    const oldParas = Array.from(container.querySelectorAll(':scope > p'));
    for (let i = 0; i < oldParas.length; i++) {
      const target = (i < newParagraphs.length) ? newParagraphs[i] : '';
      if (normalizeHTML(oldParas[i].innerHTML) !== normalizeHTML(target)) return oldParas[i];
    }
    if (newParagraphs.length > oldParas.length && oldParas.length > 0) return oldParas[oldParas.length - 1];
    return null;
  }

  // ----------------------------------------------------------
  // Branch orchestration
  // ----------------------------------------------------------

  function getReplacementForSection(branchId, sectionId) {
    const branch = window.BRANCHES && window.BRANCHES[branchId];
    if (!branch) return null;
    const affected = branch.affects && branch.affects[sectionId];
    return affected ? affected.paragraphs : null;
  }

  function ensureSectionContentWrapper(section) {
    let wrapper = section.querySelector('.section-content');
    if (!wrapper) {
      wrapper = document.createElement('div');
      wrapper.className = 'section-content';
      const mark = section.querySelector('.section-mark');
      const nodes = Array.from(section.children).filter(c => c !== mark);
      nodes.forEach(n => wrapper.appendChild(n));
      section.appendChild(wrapper);
    }
    return wrapper;
  }

  function listSectionsFromForkOnward(branchId) {
    const branch = window.BRANCHES && window.BRANCHES[branchId];
    if (!branch) return [];
    const allSections = Array.from(
      document.querySelectorAll(`section.section[id^="${BEAT_ID}-s"]`)
    ).map(s => s.id);
    const idx = allSections.indexOf(branch.fork.sectionId);
    if (idx === -1) return [];
    return allSections.slice(idx);
  }

  // Multi-section runtime fix: hide canon sections that the branch
  // does not replace AND are after the branch's affects map.
  function hideUnaffectedSections(branchId) {
    const branch = window.BRANCHES && window.BRANCHES[branchId];
    if (!branch) return;
    const sections = listSectionsFromForkOnward(branchId);
    for (const sId of sections) {
      const replacement = getReplacementForSection(branchId, sId);
      if (replacement === null) {
        const el = document.getElementById(sId);
        if (el) el.classList.add('hidden-by-branch');
      }
    }
  }
  function showAllSections() {
    document.querySelectorAll('.hidden-by-branch')
      .forEach(el => el.classList.remove('hidden-by-branch'));
  }

  async function commitBranch(branchId) {
    const branch = window.BRANCHES && window.BRANCHES[branchId];
    if (!branch) return;
    document.body.classList.add('animating');
    const pulse = document.getElementById('pulse');
    if (pulse) {
      pulse.firstChild.textContent = 'Rewriting';
      pulse.classList.add('show');
    }

    const decision = document.getElementById('decision-' + branchId);
    if (decision) decision.classList.remove('open');

    const sectionsToRewrite = listSectionsFromForkOnward(branchId);

    for (let i = 0; i < sectionsToRewrite.length; i++) {
      const sId = sectionsToRewrite[i];
      const replacement = getReplacementForSection(branchId, sId);
      if (!replacement) continue;

      if (sId === branch.fork.sectionId) {
        const postFork = document.querySelector(`.post-fork[data-fork-target="${branchId}"]`);
        if (!postFork) continue;
        if (!hasAnyChange(postFork, replacement)) continue;
        const fp = document.querySelector(`.fork-paragraph[data-fork="${branchId}"]`);
        if (fp) {
          fp.scrollIntoView({ behavior: REDUCED_MOTION ? 'auto' : 'smooth', block: 'center' });
          await sleep(REDUCED_MOTION ? 0 : 450);
        }
        await rewriteContainerParagraphs(postFork, replacement);
      } else {
        const section = document.getElementById(sId);
        if (!section) continue;
        const wrapper = ensureSectionContentWrapper(section);
        if (!hasAnyChange(wrapper, replacement)) continue;
        const firstChanged = findFirstChangedParagraph(wrapper, replacement);
        const target = firstChanged || section;
        target.scrollIntoView({ behavior: REDUCED_MOTION ? 'auto' : 'smooth', block: 'center' });
        await sleep(REDUCED_MOTION ? 0 : 500);
        await rewriteContainerParagraphs(wrapper, replacement);
      }
    }

    hideUnaffectedSections(branchId);
    setActiveBranch(branchId);
    applyBranchedUI();
    fireCodaTick();
    document.body.classList.remove('animating');
    if (pulse) pulse.classList.remove('show');
  }

  async function returnToCanon() {
    const branchId = getActiveBranch();
    if (!branchId) return;
    const branch = window.BRANCHES && window.BRANCHES[branchId];
    if (!branch) {
      setActiveBranch(null); applyBranchedUI(); return;
    }

    document.body.classList.add('animating');
    const pulse = document.getElementById('pulse');
    if (pulse) {
      pulse.firstChild.textContent = 'Restoring';
      pulse.classList.add('show');
    }

    showAllSections();

    const sectionsToRewrite = listSectionsFromForkOnward(branchId);

    for (let i = 0; i < sectionsToRewrite.length; i++) {
      const sId = sectionsToRewrite[i];
      if (sId === branch.fork.sectionId) {
        const postFork = document.querySelector(`.post-fork[data-fork-target="${branchId}"]`);
        if (!postFork) continue;
        const tmp = document.createElement('div');
        tmp.innerHTML = canonSnapshot[branchId] || '';
        const canonParas = Array.from(tmp.querySelectorAll(':scope > p')).map(p => p.outerHTML);
        if (!hasAnyChange(postFork, canonParas)) continue;
        const fp = document.querySelector(`.fork-paragraph[data-fork="${branchId}"]`);
        if (fp) {
          fp.scrollIntoView({ behavior: REDUCED_MOTION ? 'auto' : 'smooth', block: 'center' });
          await sleep(REDUCED_MOTION ? 0 : 450);
        }
        await rewriteContainerParagraphs(postFork, canonParas);
      } else {
        const section = document.getElementById(sId);
        if (!section) continue;
        const wrapper = ensureSectionContentWrapper(section);
        const fullCanon = canonSnapshot['__' + sId];
        if (!fullCanon) continue;
        const tmp = document.createElement('div'); tmp.innerHTML = fullCanon;
        const mark = tmp.querySelector('.section-mark'); if (mark) mark.remove();
        const canonParas = Array.from(tmp.querySelectorAll('p')).map(p => p.outerHTML);
        if (!hasAnyChange(wrapper, canonParas)) continue;
        const firstChanged = findFirstChangedParagraph(wrapper, canonParas);
        const target = firstChanged || section;
        target.scrollIntoView({ behavior: REDUCED_MOTION ? 'auto' : 'smooth', block: 'center' });
        await sleep(REDUCED_MOTION ? 0 : 500);
        await rewriteContainerParagraphs(wrapper, canonParas);
      }
    }

    setActiveBranch(null);
    applyBranchedUI();
    document.body.classList.remove('animating');
    if (pulse) pulse.classList.remove('show');
  }

  function applyBranchedUI() {
    const branchId = getActiveBranch();
    const status = document.getElementById('status');
    const note = document.getElementById('systemNote');
    document.querySelectorAll('.branch-mark').forEach(m => m.classList.remove('active-branch'));
    if (branchId && window.BRANCHES && window.BRANCHES[branchId]) {
      document.body.classList.add('branched');
      const name = window.BRANCHES[branchId].name;
      if (status) status.innerHTML = `Reading: <span class="branch-name">Branch · ${name}</span>`;
      const activeMark = document.querySelector(`.branch-mark[data-branch="${branchId}"]`);
      if (activeMark) activeMark.classList.add('active-branch');
      if (note) {
        note.textContent = "The system has noted your choice. The book has diverged.";
        note.classList.add('visible');
      }
    } else {
      document.body.classList.remove('branched');
      if (status) status.innerHTML = `Reading: <span class="branch-name">canon</span>`;
      if (note) { note.classList.remove('visible'); note.textContent = ''; }
    }
  }

  // ----------------------------------------------------------
  // Coda 11ms tick (Easter egg)
  // ----------------------------------------------------------

  function fireCodaTick() {
    if (REDUCED_MOTION) return;
    const tick = document.getElementById('codaTick');
    if (!tick) return;
    tick.classList.remove('show');
    void tick.offsetWidth; // restart animation
    tick.classList.add('show');
    setTimeout(() => tick.classList.remove('show'), 1500);
  }

  // ----------------------------------------------------------
  // Event wiring
  // ----------------------------------------------------------

  function wireEvents() {
    document.querySelectorAll('.branch-mark').forEach(mark => {
      mark.addEventListener('click', (e) => {
        e.stopPropagation();
        if (document.body.classList.contains('animating')) return;
        if (getActiveBranch()) return;
        const branchId = mark.getAttribute('data-branch');
        const decision = document.getElementById('decision-' + branchId);
        if (!decision) return;
        const isOpen = decision.classList.contains('open');
        document.querySelectorAll('.decision').forEach(d => d.classList.remove('open'));
        if (!isOpen) {
          decision.classList.add('open');
          setTimeout(() => decision.scrollIntoView({
            behavior: REDUCED_MOTION ? 'auto' : 'smooth', block: 'center'
          }), 200);
        }
      });
    });

    document.querySelectorAll('.decision-btn').forEach(btn => {
      btn.addEventListener('click', async (e) => {
        e.stopPropagation();
        const action = btn.dataset.action;
        const branchId = btn.dataset.branch;
        const decision = document.getElementById('decision-' + branchId);
        if (action === 'cancel') {
          if (decision) decision.classList.remove('open');
        } else if (action === 'commit') {
          if (decision) decision.classList.remove('open');
          await sleep(REDUCED_MOTION ? 0 : 450);
          await commitBranch(branchId);
        }
      });
    });

    const returnBtn = document.getElementById('returnBtn');
    if (returnBtn) {
      returnBtn.addEventListener('click', async (e) => {
        if (document.body.classList.contains('animating')) return;
        e.target.disabled = true;
        await returnToCanon();
        e.target.disabled = false;
      });
    }
  }

  // ----------------------------------------------------------
  // Bookmark — track last-visible paragraph, persist to localStorage
  // ----------------------------------------------------------

  let bookmarkTimer = null;
  let bookmarkPending = null;

  function saveBookmark(paragraphId) {
    try {
      const beatTitleEl = document.querySelector('.masthead h1');
      const beatN = parseInt((BEAT_ID || '').replace('b', ''), 10) || 0;
      const data = {
        beatId: BEAT_ID,
        beatN: beatN,
        beatTitle: beatTitleEl ? beatTitleEl.textContent.trim() : ('Beat ' + beatN),
        branch: getActiveBranch(),
        paragraphId: paragraphId,
        url: window.location.pathname,
        at: Date.now(),
      };
      localStorage.setItem(BOOKMARK_KEY, JSON.stringify(data));
    } catch (e) {}
  }

  function schedulePersist(paragraphId) {
    bookmarkPending = paragraphId;
    if (bookmarkTimer) return;
    bookmarkTimer = setTimeout(() => {
      if (bookmarkPending) saveBookmark(bookmarkPending);
      bookmarkTimer = null;
      bookmarkPending = null;
    }, 800);
  }

  function setupBookmarkTracker() {
    if (!('IntersectionObserver' in window)) return;
    const observer = new IntersectionObserver((entries) => {
      // Find the topmost paragraph currently in the viewport.
      let topmost = null;
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        const top = e.boundingClientRect.top;
        if (topmost === null || top < topmost.boundingClientRect.top) {
          topmost = e;
        }
      }
      if (topmost && topmost.target.id) {
        schedulePersist(topmost.target.id);
      }
    }, {
      // Track when a paragraph crosses the upper third of the viewport.
      rootMargin: '-20% 0px -65% 0px',
      threshold: 0,
    });

    document.querySelectorAll(`p[id^="${BEAT_ID}-s"]`).forEach(p => observer.observe(p));
  }

  function restoreFromHash() {
    const hash = window.location.hash;
    if (!hash) return;
    const id = hash.slice(1);
    if (!/^[a-zA-Z0-9-]+$/.test(id)) return;
    // Defer so branch-activation and stagger-reveal complete first.
    setTimeout(() => {
      const el = document.getElementById(id);
      if (el) {
        el.scrollIntoView({
          behavior: REDUCED_MOTION ? 'auto' : 'smooth',
          block: 'start',
        });
      }
    }, REDUCED_MOTION ? 0 : 350);
  }

  // ----------------------------------------------------------
  // Bootstrap
  // ----------------------------------------------------------

  function init() {
    captureCanon();
    wireEvents();

    // Deep-link auto-activation: URL slug overrides stored state.
    if (DEEP_LINK_BRANCH) {
      setActiveBranch(DEEP_LINK_BRANCH);
    }

    const branchId = getActiveBranch();
    if (branchId && window.BRANCHES && window.BRANCHES[branchId]) {
      // Initial render: instant swap (no animation on first paint).
      const branch = window.BRANCHES[branchId];
      const sectionsToRewrite = listSectionsFromForkOnward(branchId);
      sectionsToRewrite.forEach(sId => {
        const replacement = getReplacementForSection(branchId, sId);
        if (!replacement) return;
        const html = replacement.join('');
        if (sId === branch.fork.sectionId) {
          const postFork = document.querySelector(`.post-fork[data-fork-target="${branchId}"]`);
          if (postFork) postFork.innerHTML = html;
        } else {
          const section = document.getElementById(sId);
          if (!section) return;
          const wrapper = ensureSectionContentWrapper(section);
          wrapper.innerHTML = html;
        }
      });
      hideUnaffectedSections(branchId);
      applyBranchedUI();
    }

    // Reveal article (was hidden during initial setup to avoid flicker).
    const article = document.getElementById('article');
    if (article) article.classList.add('stagger-reveal');

    setupBookmarkTracker();
    restoreFromHash();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
