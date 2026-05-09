# Audit — Branch Logic (W1.1)

**Agent:** branch-logic-engineer
**Subject:** `prototype/index-v4.html` JS — branch state, localStorage, decision cards, marginal marks, reset.
**Reference:** `ledger.md` §1.2; `process/workflow.md`; agent definition (state machine, hard rules).
**Verdict at a glance:** prototype works for the 3-branch demo. The shape is broadly right, but the explicit `canon | transitioning | branch_<id>` state machine isn't named in code; switch-via-canon and accessibility have gaps; and the `BRANCHES` object format is bespoke, not the workflow.md schema. None of this is fatal — all are clean refactors.

---

## 1. State machine

**Current:** state lives in two places — `state.branch` (`null` or branch id) and DOM classes on `<body>` (`branched`, `animating`). There is no explicit `transitioning` value; the animation lock is implied by the `animating` class plus an early-return guard. There is no named `STATE` constant or transition function.

**Transitions in code:**
- `canon → branch_X`: `commitBranch(branchId)` — runs the forward animation, then sets `state.branch` and `applyBranchedUI()`. State is set *after* the animation, which means a reload mid-animation persists nothing (acceptable, but worth noting).
- `branch_X → canon`: `returnToCanon()` — symmetrical.
- `branch_X → branch_Y`: **not supported.** The branch-mark click handler bails on `if (state.branch) return;` and `body.branched .branch-mark { ... display: none }` hides the marks anyway. So the reader cannot move A→B at all, let alone via canon.

**Verdict:** Partial.
- Works: forward and reverse transitions; mutual exclusion via the `animating` class; the on-screen "this branch is active" mark is suppressed.
- Missing: explicit named states; the `branch_X → canon → branch_Y` switch path; a single-source-of-truth state setter that gates transitions and persists atomically.

**Recommendation:** introduce a `STATE = { value: 'canon' | 'transitioning' | 'branch_<id>' }` plus a `setState()` that (a) rejects illegal transitions, (b) calls `saveState()` only when settling on a non-transitioning state, (c) drives the `<body>` classes. Keep `state.branch` as a computed projection for persistence (`branch: STATE.value === 'canon' ? null : id`).

---

## 2. localStorage persistence

**Stored:** `localStorage['forest-state-v4'] = JSON.stringify({ branch: 'b1' | null })`. Matches the agent contract.

**Restored on load:** the IIFE at bottom calls `loadState()` then, if `state.branch && BRANCHES[state.branch]`, snaps the post-fork div and downstream sections to the branch HTML *without* animation, and runs `applyBranchedUI()`. Correct behaviour: restoration must be silent, not a flap.

**Stale / removed branch id:**
- `loadState` accepts whatever JSON it reads; does not validate `state.branch` against `BRANCHES`.
- The init block guards with `if (state.branch && BRANCHES[state.branch])` and silently falls through if the id is unknown — but **does not clear** the persisted value. On the next save (e.g. selecting a real branch), the bad id is overwritten, but until then it sits in localStorage.
- `returnToCanon()` early-returns if `!state.branch`, so a stale id can't be cleared via the reset path either.

**Corrupt JSON:** `loadState` swallows exceptions; `state` keeps its initial `{ branch: null }`. Good.

**Verdict:** Partial.
- Works: storage key, shape, restore, silent rehydration, corrupt-JSON tolerance.
- Missing: explicit prune of unknown branch ids ("fail gracefully back to canon and clear the persisted value" — agent rule).

**Recommendation:** in `loadState()`, after parsing, validate `state.branch` against `BRANCHES`. If it isn't a key (or is otherwise malformed), set `state.branch = null` and call `saveState()` immediately. Same check before the init's restore branch.

---

## 3. Decision card

**Open:** click on a `.branch-mark` toggles `.decision.open` on the matching `#decision-<id>` element. All other decision cards are closed first. After 200 ms, the card is scrolled into center view.

**Close:** the "Stay with canon" button removes `.open`. The "Follow this branch" button removes `.open`, waits 450 ms, then runs `commitBranch`. There is **no Esc-to-close, no click-outside-to-close, no second click on the same mark to close** — wait, the toggle logic does support second-click-to-close (`if (!isOpen) decision.classList.add('open')`), so re-clicking the mark closes the card. Good.

**Content source:** the decision card markup is **hardcoded in HTML**, not pulled from `BRANCHES`. The `decision-title` ("Branch · The Fourth Opinion") and `decision-summary` text are duplicated between the inlined HTML and `BRANCHES.b1.name`. Drift risk.

**Mouse vs keyboard:**
- The marginal mark is a real `<button>` with `aria-label`. Tab-focusable, Space/Enter activates. Good.
- Decision buttons are `<button>` elements. Good.
- **Focus management is missing.** Opening the card does not move focus into it; closing the card does not return focus to the mark. A keyboard reader has to tab from the mark, through the page, to reach "Follow this branch."
- No Esc handler.
- The decision card uses `max-height: 0; overflow: hidden;` but does not set `aria-hidden` or `inert` when collapsed, so the buttons inside are reachable in the tab order even when invisible.

**Verdict:** Partial.
- Works: open/close UX for mouse users; ARIA label on the mark.
- Missing: focus into card on open; focus restore on close; Esc-to-close; `inert`/`aria-hidden` on closed cards; content sourced from `BRANCHES`.

**Recommendation:** populate `.decision-title` / `.decision-summary` from `BRANCHES[id].name` and a new `summary` field at init. On open, focus the primary button. On close (any path), focus the originating mark. Add `inert` to all `.decision` elements; remove on open. Add a global Esc handler.

---

## 4. Marginal mark click

The mark only opens/closes the decision card. No other behaviour. There is a `.branch-mark:hover .label` reveal that exposes the word "branch" — purely visual. Marks become `pointer-events: none` while `body.animating`, and are hidden / inactive (`opacity: 0; display: none`) once any branch is active.

**Verdict:** Works for the canonical case (canon → click → card opens). Missing: marks are not interactive at all when in a branch state, which forecloses the A→B switch path (see §6).

---

## 5. Reset action

**Implementation:** a single `<button id="returnBtn" class="return-to-canon">` in the masthead. Hidden by default; CSS reveals it via `body.branched .return-to-canon { display: inline-block }`. Click handler disables the button, awaits `returnToCanon()`, re-enables.

**Reachable from anywhere?** It sits in the masthead at the top of the document. From mid-chapter, the reader must scroll up. Workflow.md and the agent contract require the reset to be reachable from anywhere in the reading flow; a button that requires scroll-to-top is reachable but not present.

**Verdict:** Partial.
- Works: single-click return; disable-during-animation guard; correct visibility coupling.
- Missing: in-flow reachability. A sticky / floating control, or a footer-mirrored control, would close the gap. Coordinate with `html-css-architect`.

**Also worth fixing:** the button ↺ label is fine, but is hidden by `display: none` when not branched — keyboard users will skip past it on tab anyway, so no a11y harm; just confirm with a11y review when the sticky variant lands.

---

## 6. One-branch-at-a-time

**Enforced?** Yes — but by foreclosure, not by the switch-through-canon path the agent contract specifies.
- `branch-mark` click: `if (state.branch) return;` (guard #1).
- `body.branched .branch-mark { ... display: none }` (guard #2; CSS).
- The active mark also gets `.active-branch` which sets `display: none`.

So once branch A is active, B's mark is non-clickable and visually suppressed. The reader must explicitly hit Return-to-canon, then click B's mark, then commit.

**Switch via canon:** in the agent contract, selecting B while A is active is a single intent that drives `branch_A → transitioning(canon) → canon → transitioning(branch_B) → branch_B`. In code this is two separate user actions, not one. Two clicks instead of one is not a correctness problem — it's a UX gap and a contract gap.

**Verdict:** Partial.
- Works: no stacking; one branch at most; guards are robust.
- Missing: the one-click switch path. To enable it, marks must remain reachable in branch state (perhaps with a subtler "switch to this branch" affordance), and the click handler must orchestrate `returnToCanon().then(() => commitBranch(otherId))`.

**Recommendation:** keep marks visible-but-secondary while branched (the workflow.md schema's `affects` map makes it possible to identify which paragraphs would change vs which would not — that's a separate signal). Click-on-other-mark = open *that* branch's decision card; commit triggers a chained reverse-then-forward animation through canon.

---

## 7. Initial load

**Path:** `captureCanon()` snapshots both the post-fork divs (keyed by branch id) and full sections (keyed by `__<sectionId>`). Then `loadState()`. If `state.branch` is a known id, paragraphs are written via `innerHTML = html` (no animation).

**Failure modes:**
- **Stored id no longer in BRANCHES:** the init block silently falls through; no animation, no error, but the persisted bad id is *not* cleared (see §2).
- **Corrupt JSON:** swallowed, defaults to canon. Good.
- **localStorage disabled / quota exceeded:** `saveState`'s try/catch silently swallows. Reader will get canon-only behaviour. Acceptable; worth a console.warn for debuggability.
- **`captureCanon` runs before BOM is fully ready?** The script is at body-end and the IIFE runs synchronously. Fine for the inlined-HTML model. If the build later defers any DOM, this becomes load-order-sensitive.
- **Restored content gets out of sync if HTML/canon prose is later edited:** because `canonSnapshot` is taken from the live DOM at script load, this is robust to canon edits between builds. Good.

**Verdict:** Mostly works. Main gap is the stale-id cleanup.

---

## 8. BRANCHES object

**Current shape (per file):**
```js
b1: {
  name: "The Fourth Opinion",
  section: "s1",                 // fork section
  s1_replacement: [ "<p HTML>", ... ],   // post-fork replacement, this section
  downstream: [
    { section: "s2", paragraphs: [ ... ] },
    ...
  ]
}
```

The fork *paragraph* is implicit — the data-fork attribute on the `<p>` and the matching `data-fork-target` on the `<div class="post-fork">` carry it in the HTML. The `section` field on the JS object names only the section. The replacement is a flat array of paragraph HTML strings; "from-paragraph" is implicit (always paragraph-after-fork for the fork section, always paragraph-1 for downstream sections).

**Workflow.md target shape (per assignment brief):**
```
{
  id, name, summary,
  fork: { sectionId, afterParagraph },
  affects: {
    sectionId: { fromParagraph, paragraphs[] }
  }
}
```

This explicit form has three advantages:
1. `summary` is the source for the decision card text — currently duplicated in HTML.
2. `affects` is uniform across fork-section and downstream sections; today the code special-cases `s1_replacement` vs `downstream[i].paragraphs`.
3. `fromParagraph` lets a downstream branch start mid-section, which the current schema cannot express (it always replaces from paragraph 1).

**Alignment:** Misaligned.
- Works: round-trips for the prototype's three branches because they happen to follow the implicit conventions.
- Missing: `id` (key suffices but is redundant when iterating); `summary`; `fork.afterParagraph` (paragraph-id, not just section); `affects[s].fromParagraph`; uniform `affects` map.

**Recommendation:** rewrite `BRANCHES` to the workflow.md schema before more branches land. The build engineer's `build/build.py` will likely emit this shape natively. Branch logic then becomes:
- `getReplacementForSection(branch, sectionId)` returns `branch.affects[sectionId]` directly.
- Decision card content is `branch.name` + `branch.summary`.
- Fork-paragraph DOM lookup uses `branch.fork.afterParagraph` (paragraph id, e.g. `p-s1-5`) — more robust than today's section-only key.

---

## Cross-cutting recommendations (priority order)

1. **Adopt the workflow.md `BRANCHES` schema.** Largest leverage. Coordinate with `build-engineer`; this changes both producer and consumer.
2. **Validate persisted branch id on load and clear if unknown.** Cheap fix; closes a hard-rule gap.
3. **Source decision card content from `BRANCHES` (after #1).** Removes drift surface.
4. **Implement true switch-via-canon (one-click A→B).** Aligns code with the project rule; keeps reset semantics intact.
5. **Sticky / always-reachable reset control.** Coordinate with `html-css-architect`.
6. **Decision card a11y: focus management, Esc-to-close, `inert` on closed cards.**
7. **Name the state machine in code (`STATE.value`, `setState()`).** Lower priority than the above but pays back in test legibility.

## Out of scope for this audit / agent

- Animation timing, cascade, performance — see `animation-engineer` audit.
- Visual treatment of marginal marks, sticky reset placement, decision card styling — `html-css-architect`.
- Build pipeline that emits `BRANCHES` — `build-engineer`.

No changes implemented in this audit, per instructions.
