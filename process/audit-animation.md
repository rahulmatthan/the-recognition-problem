# Animation Audit — `prototype/index-v4.html`

**Auditor:** animation-engineer
**Date:** 2026-05-03
**File audited:** `/Users/rahul/Coding/recognition-forest/prototype/index-v4.html` (1016 lines, three sections, three branches `b1`, `b2`, `b3`).
**No code changes made. This is read-only.**

The prototype demonstrates a working split-flap rewrite with diff-aware paragraph detection and a cascading overlap. The architecture is sound for a 3-branch, 3-section demo. Several behaviours diverge from the project rules in `ledger.md` §1.2 and `process/quality-gates.md` §3 — most importantly **one-branch-at-a-time enforcement** and **scroll-to-first-changed-paragraph**. Performance is acceptable at the prototype scale but has structural concerns that will surface at the 23-branch / 140k-word scale.

---

## 1. Split-flap implementation

**Status: works.**

### How it works
The animation is implemented in `flapParagraph()` (lines 546–625). For each paragraph that needs to change:

1. The function pads `oldText` and `targetText` to the same length using trailing spaces (line 558–559).
2. The `<p>` gets `class="flapping"` (mono font, smaller size — see CSS lines 185–198).
3. The paragraph's `innerHTML` is replaced with a flat sequence of `<span class="flap-ch">` — one span per character (lines 568–581). Italics, embedded `<span>`s, and the coda `<span class="branch-coda-line">` are flattened to plaintext for the duration of the animation.
4. Each span gets a randomised flip count between `MIN_FLIPS=5` and `MAX_FLIPS=22` (lines 525–526, 578).
5. A single `setInterval` running at `TICK_MS=50` (line 524) iterates every span and either substitutes a random char from `FLAP_CHARS` (`a–zA–Z.,;:—`, line 523) or — if the span has run out of flips — settles it to its target character and adds `.settled` (lines 587–600).
6. When all spans settle, a 180 ms pause then restores the real `targetHTML` so italics and embedded spans return (lines 612–621).

### Character cell DOM strategy
- One `<span class="flap-ch">` per character.
- Fixed slot width via `min-width: 0.58ch` and `text-align: center` (CSS lines 206–214). `font-variant-numeric: tabular-nums` keeps digits aligned.
- During flap: branch ochre colour (`var(--branch)`); after settle: ink colour. A subtle `text-shadow` pulses while flapping (lines 220–223).
- Wrapping is forced via `word-break: break-word; overflow-wrap: anywhere` (lines 196–197) — this prevents the cascade from blowing past the column width but produces ugly mid-word wraps during the flap. It resolves once `flapping` is removed.

### Transition CSS
- `.flap-ch` has `transition: color 0.18s ease` — only the colour transitions on settle. The character itself swaps via `textContent` assignment, not via a CSS transform. There is no 3D flap animation; the airport-board feel comes from the rapid character substitution at 50 ms intervals.

### Verdict
Mechanically correct and visually convincing for short paragraphs. **Concerns** (covered in §6 below): one `setInterval` per paragraph, one DOM span per character, full `innerHTML` flatten/rebuild per paragraph.

---

## 2. Diff-aware logic

**Status: works as needed at section granularity; partial at paragraph granularity.**

The prototype computes diffs at **paragraph level**, not character level.

### Where
- `normalizeHTML(html)` (lines 638–642) — parses through a temp `<div>` and collapses whitespace so HTML formatting differences don't trigger false diffs.
- `rewriteContainerParagraphs()` (lines 657–715) — for each old paragraph against its index-aligned target, computes `flapsNeeded[i] = currentNorm !== targetNorm` (lines 673–678). Only paragraphs marked `true` participate in the cascade chain (line 690).
- `hasAnyChange()` (lines 721–730) and `findFirstChangedParagraph()` (lines 737–750) — used upstream by `commitBranch` and `returnToCanon` for skip-section and scroll decisions.

### What works
- Identical paragraphs hold still — confirmed by reading `rewriteContainerParagraphs` lines 689–690 (`if (!flapsNeeded[i]) continue`).
- Sections with no changes are skipped entirely (`commitBranch` lines 808, 824).
- Paragraph count changes are handled: pad with empty `<p>` if growing (lines 663–667); flap to blank then `.remove()` if shrinking (lines 702–705).

### What is partial
- **Diff is index-aligned, not content-aligned.** If a branch inserts a new paragraph at position 2, every paragraph from index 2 downward is treated as "changed" because their indices have shifted, even though their content might be identical to a former position. For the current 3 branches this isn't visible (each branch's replacement list is fully rewritten prose), but for surgical branches with only one or two changed paragraphs in a long list, this will over-flap.
- **No character-level diff inside a paragraph.** A paragraph that changes one word still flaps every character. Given the project's "branch is a rewrite, not a tweak" principle (ledger §1.2), this is probably *correct* — most branch paragraphs differ substantially. But for branches whose first paragraph after the fork keeps the canon's opening sentence and diverges mid-paragraph, the whole paragraph re-flaps.

### Recommendation
- Keep paragraph-level diff as the primary mechanism (matches the principle that branch is a rewrite).
- Consider a content-aligned diff (LCS over normalized paragraph hashes) so that index-shifts don't cascade false positives. Cheap to compute over ~30 paragraphs.

---

## 3. Cascade timing

**Status: works.**

- `PARAGRAPH_OVERLAP = 0.55` (line 527).
- `flapParagraph` exposes an `onNearDone` callback fired when elapsed time reaches `expectedDuration * PARAGRAPH_OVERLAP`, where `expectedDuration = MAX_FLIPS * TICK_MS = 22 × 50 = 1100 ms` (lines 583–607).
- `rewriteContainerParagraphs` chains promises via `nextStartPromise` so paragraph N+1 starts when N's near-done callback fires (lines 686–712).
- The cascade chain is built **only over flapping paragraphs** (line 690), so identical paragraphs neither animate nor block.

### Tunable
- `TICK_MS`, `MIN_FLIPS`, `MAX_FLIPS`, `PARAGRAPH_OVERLAP` are top-of-script constants (lines 523–527) — easy to tune.
- However, `expectedDuration` is hard-coded as `MAX_FLIPS * TICK_MS`. If a paragraph's actual flip count is short (because all spans land early), the near-done timing is tied to the worst case rather than the actual paragraph length. For very long paragraphs the cascade may be too fast (next paragraph starts before the current is visually substantial); for short paragraphs the next start may already have fired before any flips are visible.

### Recommendation
Compute `expectedDuration` per paragraph from its actual `len * TICK_MS`-equivalent floor, or fire `onNearDone` based on settle progress (e.g. when 55% of spans are settled) rather than wall-clock.

---

## 4. Scroll-to-first-changed-paragraph

**Status: works partially.**

### Fork-section (the section containing the chosen branch)
- `commitBranch` scrolls to `.fork-paragraph[data-fork="${branchId}"]` with `block: 'center'`, then waits 450 ms (lines 811–815). This scrolls to the **fork paragraph** — the paragraph with the marginal mark — not the first paragraph that changes. The fork paragraph is the *last unchanged* paragraph (it's preserved verbatim from canon as a fork anchor); the first changed paragraph is the first `<p>` inside the `.post-fork` div directly below it.
- For typical reader posture (mark clicked, decision card open in centre), the fork paragraph is already visible. Centring on it again is mostly a no-op. The visual effect: the mark stays where it is, the post-fork content below begins flapping.

### Downstream sections (sections after the fork section)
- `commitBranch` calls `findFirstChangedParagraph(wrapper, replacement)` and scrolls to that paragraph (lines 827–829). For downstream sections this is correct — the function returns the first index where `normalizeHTML` of current ≠ target. For the current 3 branches, the entire downstream section is replaced, so this lands on the first paragraph of the section.

### What's missing / fragile
- **Above-viewport case:** `scrollIntoView({ behavior: 'smooth', block: 'center' })` works in both directions. Smooth scroll *up* is supported on Chrome and Safari. No tested concern.
- **Between-section case:** if a branch only changes the post-fork in `s1` and one paragraph in `s3` (skipping `s2`), the reader sees `s1` rewrite, then a 500 ms wait, then a smooth scroll to deep `s3` — but `s2` is **not** scrolled past in any visible way. The scroll just jumps the reader past unchanged material. This may be the desired behaviour (don't scroll through unchanged text) but is worth confirming with the design lead. The fork-paragraph mark is also lost from view if the reader doesn't re-scroll up after.
- **Smooth-scroll race:** the `await sleep(450)` (line 814) and `await sleep(500)` (line 830) are timing-based. If a slow device hasn't completed the smooth scroll in that window, the flap starts before the target paragraph is visible. There's no `scrollend` event being awaited.
- **Decision-card scroll** at line 951 (`setTimeout 200 ms` then `scrollIntoView({ block: 'center' })`) competes briefly with the imminent commit scroll. Not visibly broken in the prototype but worth tightening.

### Recommendation
For fork-section commits, scroll to the **first `<p>` inside `.post-fork`**, not the fork paragraph itself. Replace `await sleep(450)` with a `scrollend` Promise (with a `setTimeout` fallback). Decide explicitly whether downstream-section scrolling should pass *through* skipped sections or jump them.

---

## 5. One-branch-at-a-time enforcement

**Status: works partially. The "go through canon first" rule is NOT enforced.**

### What's enforced
- The branch-mark click handler (lines 939–954) checks `if (state.branch) return` — so once a branch is active, *clicking another branch mark* is a no-op. The marks are also visually disabled via `body.branched .branch-mark { pointer-events: none; opacity: 0.25 }` (line 145).
- `applyBranchedUI` adds `active-branch` to the chosen mark and hides it (lines 148, 922–923).

### What is NOT enforced (project rule violation)
The animation-engineer agent definition says:

> **One branch active at a time.** Switching from branch A to branch B goes through canon first — animation runs back to canon, then forward to B. Two animations, not one direct flip.

The current code makes A→B switching **impossible from the UI** (marks are disabled while branched). The reader must click "Return to canon" first, *then* click branch B. There is no helper that performs `returnToCanon()` then `commitBranch(B)` in sequence.

This is a soft form of compliance: the rule technically holds because you can't go directly. But the reader-facing behaviour is "you must reset before switching," which adds friction. The intended behaviour per the agent definition is "selecting B while A is active runs A→canon then canon→B as two visible animations."

### Recommendation
- Either: keep the current friction-style enforcement and update the agent definition to reflect it.
- Or: when a branch is active and a mark for a different branch is clicked, automatically run `returnToCanon()` then `commitBranch(B)` in sequence. The two-animation sequence is the documented behaviour.

---

## 6. Performance

**Status: works at prototype scale; concerns at full scale.**

### Frame-budget rough estimate (current prototype)
- Per paragraph: one `setInterval` at 50 ms; per tick, every span (one per character) gets a `textContent` assignment. A typical branch paragraph in v4 is ~600 characters → 600 spans → 600 textContent writes per tick. With `PARAGRAPH_OVERLAP = 0.55`, up to 2 paragraphs run concurrently → ~1,200 writes per tick → ~24 writes/ms.
- Modern browsers batch text-only updates well; this should comfortably hold 60 fps for 1–2 concurrent paragraphs of this size on a modern laptop.

### Concerns at 23-branch / ~140k-word scale
1. **DOM size at rest.** `BRANCHES` is a literal in the script — at 23 branches each with full prose for affected sections, the script payload is the dominant page weight. At 140k words across canon + 23 branches, a conservative estimate is 1–2 MB of HTML/script, all in one file. Parse and JS evaluation on first load become the bottleneck, not the animation.
2. **`.post-fork` and section-content snapshotting.** `captureCanon()` (lines 509–517) stores `innerHTML` per `.post-fork` and per section. With 23 forks across 10 chapters, snapshot memory is bounded but the `innerHTML` round-trips during commit/return are non-trivial.
3. **Span proliferation during cascade.** On a section-wide rewrite, every paragraph spawns a span-per-character. A 4,000-character section → 4,000 spans created and torn down per branch select. The current 180 ms post-settle pause + `pElement.innerHTML = targetHTML` (line 614) is the cleanup; this triggers a layout invalidation per paragraph.
4. **Cascade chain complexity.** With surgical branches (e.g. coda-only, two paragraphs changed in a long section), the chain is fine. With full-section rewrites, the cascade may run 6–10 paragraphs deep — a 1100 ms × 0.45 stagger × 8 paragraphs ≈ 4 s of animation. Reader patience and 60 fps simultaneity must both hold across that window.
5. **`setInterval` instead of `requestAnimationFrame`.** `TICK_MS=50` is 20 Hz, well under display refresh. Frame jitter is invisible at this rate. But `setInterval` is throttled in background tabs and skewed by main-thread blocking. `requestAnimationFrame` with a tick accumulator would be more predictable.
6. **Random char generator.** `FLAP_CHARS = 'a–zA–Z.,;:—'` — 56 characters. Each span calls `Math.floor(Math.random() * 56)` per tick. Cheap, but multiplied by thousands of writes per second it's measurable. Pre-compute a lookup or batch random.

### Recommendation (prioritised)
- Profile a worst-case branch (full section-wide rewrite, longest paragraph) on a modest laptop before optimising.
- If frame budget is tight: replace `setInterval` with `requestAnimationFrame` and drive all paragraphs from a single ticker.
- If memory is tight at 23 branches: keep branch prose in the script but lazily mount HTML for branches not yet selected.
- Don't pre-optimise span pooling unless profiling shows GC pauses.

---

## 7. Reset action

**Status: works. Symmetric with commit.**

- `returnToCanon` (lines 844–907) mirrors `commitBranch`: same section iteration, same `hasAnyChange` skip, same `findFirstChangedParagraph` scroll, same `rewriteContainerParagraphs` flap.
- The pulse text changes from "Rewriting" to "Restoring" (line 852).
- `state.branch = null` and `applyBranchedUI` runs at the end (lines 901–903).
- Per the agent definition: "Reset returns to canon with the animation running in reverse-direction." The current implementation **runs forward** — the same character-flap, in branch→canon direction. There's no visual cue that the animation is "rewinding" beyond the pulse label change. Whether this counts as "reverse-direction" depends on interpretation: the *content* is reversing (you're going back to canon), but the *animation mechanism* (random flips converging on target) is identical.

### User experience of resetting
- Reader clicks "Return to canon" in the header.
- Button is `disabled` during animation (line 975) — prevents double-click.
- Pulse shows "Restoring."
- Page scrolls to the fork paragraph in the fork section. Post-fork div animates back to canon. Then downstream sections rewrite.
- Branched UI removes (header colour returns to ink, mark visibility restores).
- Reader is now at the fork section, mid-page. The decision-card mark is restored at top-right and clickable again.

### Recommendation
- If the design intent is "reverse-direction" in a literal sense (target → random → original, instead of random → target), this needs an explicit reversed-flap variant. Worth confirming with `html-css-architect` and the design lead.
- Otherwise the current behaviour is fine but should be documented as "reset uses the same forward-flap, in the branch→canon direction." Update the agent definition if interpretation differs.

---

## Summary table

| # | Item | Status | Severity |
|---|---|---|---|
| 1 | Split-flap implementation | Works | — |
| 2 | Diff-aware (paragraph-level) | Works | — |
| 2 | Diff-aware (content-aligned) | Partial | Low |
| 3 | Cascade timing | Works | — |
| 3 | Per-paragraph timing tunability | Partial | Low |
| 4 | Scroll on commit (fork section) | Partial — scrolls to fork ¶, not first changed ¶ | Medium |
| 4 | Scroll on commit (downstream) | Works | — |
| 4 | `scrollend` not awaited | Partial | Low |
| 5 | One-branch-at-a-time (no overlap) | Works | — |
| 5 | A→B routes through canon | **Not implemented** — switching is blocked, not chained | Medium |
| 6 | 60 fps at prototype scale | Likely works | — |
| 6 | 60 fps at 23-branch scale | Unproven; needs profiling | Medium |
| 7 | Reset action functional | Works | — |
| 7 | Reset is "reverse-direction" | Ambiguous | Low |

---

## Top three changes proposed (no implementation)

1. **A→B chained animation** — when a branch is active and a different branch's mark is clicked (need to re-enable mark clicks while branched, or surface them via the decision card), auto-run `returnToCanon()` then `commitBranch(newBranchId)` in sequence. This implements the project rule literally.
2. **Scroll-to-first-changed-paragraph in the fork section** — change the fork-section scroll target from the fork paragraph to the first `<p>` inside `.post-fork`. Replace the `await sleep(450)` with a `scrollend` Promise plus a 700 ms safety timeout.
3. **Performance gate before scaling to 23 branches** — profile the prototype with synthetic 4,000-character paragraphs and a 30-paragraph section to validate 60 fps. If `setInterval`-based ticking is a hotspot, refactor to a single `requestAnimationFrame` ticker driving all spans from a flat array.
