# Recognition Forest — Status

*Updated by the orchestrator. Read this first when picking up the project.*

## Phase

**Phase 2 — Parallel execution.** Phase 1 approved 2026-05-03. **Phase 2.1 + 2.2 + 2.3 + 2.4 complete (2026-05-08)** — all 23 narrative branches locked.

**Website rebuild (2026-05-09 — 2026-05-10).** Per `process/architecture-v2.md`. Single-file HTML harness rewritten as a multi-page static site at `dist/`: 10 canon chapter pages + 23 branch deep-links + intro slideshow + 6 Making essays. Self-hosted Newsreader / IBM Plex Sans / IBM Plex Mono. Persistent slide-in sidebar TOC. Bookmark-on-scroll persisted to localStorage. Multi-section runtime issue resolved by per-beat page architecture. Pending: GitHub Pages deploy with custom domain.

## Phase 1 progress

- [x] Step 1.1 — Reading + comprehension confirmation (2026-05-03)
- [x] Step 1.2 — Folder structure created (2026-05-03)
- [x] Step 1.3 — Voice profile + architectural threads written (2026-05-03)
- [x] Step 1.4 — Agent roster (9 agents at `.claude/agents/`) (2026-05-03)
- [x] Step 1.5 — Workflow at `process/workflow.md` (2026-05-03)
- [x] Step 1.6 — Quality gates at `process/quality-gates.md` (2026-05-03)
- [x] Step 1.7 — CLAUDE.md written + Phase 1 approved (2026-05-03)

## Phase 2 progress

**Phase 2.1 — Voice-finding (4 branches):**
- [x] b1-walk — **Locked 2026-05-03** (voice + arch reviews PASS; FLAGs accepted)
- [x] b8-tell — **Locked 2026-05-03** (final ~720; FLAGs addressed via surgical cuts per option B)
- [x] b2-kano — **Locked 2026-05-07** (orchestrator-direct draft on revised shifted-weight ledger; ~1,560 prose + ~270 coda; voice/arch/coda reviews skipped per Rahul)
- [x] b7-say-no — **Locked 2026-05-07** (orchestrator-direct; ~1,403; voice/arch reviews skipped per Rahul)

**Out-of-phase drafting (parallel with b2-kano per Rahul's 2026-05-06 instruction):**
- [x] b1-repair (Phase 2.2) — **Locked 2026-05-07** (orchestrator-direct draft on revised shifted-weight ledger; ~1,205; voice/arch reviews skipped per Rahul)
- [x] b9-continue (Phase 2.3) — **Locked 2026-05-07** (orchestrator-direct draft on revised section-XI-replaced ledger; ~1,480 prose + ~410 coda; voice/arch/coda reviews skipped per Rahul)

**W1 — Web foundation audits complete; awaiting Rahul's decisions:**
- [x] `html-css-architect` audit at `process/audit-html-css.md` (2026-05-03)
- [x] `animation-engineer` audit at `process/audit-animation.md` (2026-05-03)
- [x] `branch-logic-engineer` audit at `process/audit-branch-logic.md` (2026-05-03)
- [x] `build-engineer` audit at `process/audit-build.md` (2026-05-03)

## Branch status (24 entries — 23 branches + 1 reserved)

| Branch | Beat | Length target | Status |
|---|---|---:|---|
| b1-carsick | 1 | ~3,000 | **Locked 2026-05-07** (final ~3,050) |
| b1-walk | 1 | ~1,500 | **Locked 2026-05-03** |
| b1-repair | 1 | ~1,200 | **Locked 2026-05-07** (final ~1,205) |
| b2-calibrated | 2 | ~3,000 | **Locked 2026-05-07** (final ~2,570) |
| b2-kano | 2 | ~1,500 | **Locked 2026-05-07** (final ~1,830 incl. coda) |
| b3-noriko | 3 | ~3,500 | **Locked 2026-05-08** (final ~3,374) |
| b3-mother | 3 | ~2,000 | **Locked 2026-05-07** (final ~1,866) |
| b4-bodycount | 4 | ~2,000 | **Locked 2026-05-08** (final ~2,614) |
| b4-graceholds | 4 | ~1,000 | **Locked 2026-05-07** (final ~1,351) |
| b5-fourth | 5 | ~5,500 | **Locked 2026-05-08** (final ~3,900 after coda meta-cut) |
| b5-reset | 5 | ~3,500 | **Locked 2026-05-08** (final ~2,824; local-scope; terminal trajectory deferred) |
| b5-tenyear | 5 | ~2,500 | **Locked 2026-05-07** (final ~2,415) |
| b6-reset | 6 | ~6,000 | **Locked 2026-05-08** (final ~5,000; B7 proleptic-line override retained) |
| b6-visit | 6 | ~2,500 | **Locked 2026-05-07** (final ~2,750) |
| b7-tell-julien | 7 | ~5,000 | **Locked 2026-05-08** (final ~4,051) |
| b7-say-no | 7 | ~1,500 | **Locked 2026-05-07** (final ~1,403) |
| b8-failed | 8 | ~3,500 | **Locked 2026-05-08** (final ~2,967) |
| b8-tell | 8 | ~500 | **Locked 2026-05-03** (final ~720) |
| b9-restraint | 9 | ~7,000 | **Locked 2026-05-08** (final ~7,200; section-by-section inline review; Yosafat non-event cut) |
| b9-continue | 9 | ~1,500 | **Locked 2026-05-07** (final ~1,890 incl. coda) |
| b10-decline | 10 | ~5,000 | **Locked 2026-05-08** (final ~4,259) |
| b10-sushma | 10 | ~2,500 | **Locked 2026-05-07** (final ~2,505) |
| b10-lie | 10 | ~1,500 | **Locked 2026-05-08** (final ~2,017) |

Statuses: `Not started` | `Draft v1` | `In voice review` | `In arch review` | `In coda review` | `Pending Rahul` | `Locked`

## Build status

- `build/build.py` — written 2026-05-03 (1,466 lines, mistune + PyYAML)
- `build/recognition-problem.html` — current output 550.1 KB; 8 locked branches integrated (b1-walk + b1-repair + 3 b1-stub-* + b2-kano + b8-tell + b9-continue); idempotent; self-contained verified
- `prototype/index-v4.html` — system fonts + drawer TOC + paper-temperature shading implemented (2026-05-03); BRANCHES schema migrated; reset-then-select dynamic confirmed
- **Multi-section runtime issue documented (deferred to Phase 2.4 per Rahul 2026-05-07).** Static analysis of the rendered HTML's runtime JS shows that `commitBranch` only rewrites sections present in a branch's `affects` map; for any post-fork canon section *not* in `affects`, it does `continue` and leaves canon visible. `body.branched` CSS only changes accent colours — no `display: none` for unaffected sections. Effect: every locked branch (b1-walk, b1-repair, b2-kano, b8-tell, b9-continue) is terminal-shape but renders with canon's later sections still visible below the branch — two codas, two endings, and (for b9-continue) two Section XIs. Canon source is untouched (md5 verified; mtimes 30 Apr). The fix is small (~10 lines of JS): in `commitBranch`, when iterating sections-from-fork-onward, hide any section without a replacement; restore in `returnToCanon`. **Holding the fix until all 23 branches are drafted** — if any later branch is rejoining-shape rather than terminal-shape, the fix needs different machinery, so we want the full set first. Browser-test for all locked branches is therefore deferred to Phase 2.4 (single batched pass).

## Open decisions for Rahul

*All prior open decisions resolved 2026-05-07:* b1-repair ledger revision approved + drafted + locked; b9-continue ledger revision approved + drafted + locked; b2-kano redraft authorized + drafted + locked. Reviewers (voice/arch/coda) skipped per Rahul on all three. No open decisions outstanding.

## Test runs

### 2026-05-07 — Build verification post b1-repair / b2-kano / b9-continue lock

- `python3 build/build.py` succeeded; output 550.1 KB (sha256 9a31d08c…); idempotent re-run produces byte-identical output.
- All 8 locked branches integrated and fork-verified: b1-walk → b1-s8-p12, b1-repair → b1-s9-p8, b1-stub-{coda,downstream,fork} (placeholders), b2-kano → b2-s6-p21, b8-tell → b8-s11-p10, b9-continue → b9-s15-p46.
- All three new locks (b1-repair, b2-kano, b9-continue) drafted directly by orchestrator after a four-failure subagent cascade (three watchdog stalls + one 529 Overloaded). Voice/arch/coda reviews skipped per Rahul's instruction. §B.6 story-divergence test passed inline at draft time.
- One build-time fix: b9-continue's initial fork_at had italic asterisks around the system's speech; the build normaliser strips italic, so the asterisks were removed from frontmatter to satisfy the character-for-character match. No other rework.
- `data-branch` count check: 6 (3 branches × 2 sites — mark + decision card — = 6, consistent with how marks/cards are spliced).
- Browser-required tests deferred (animation, localStorage, decision card UX, scroll-to-fork, console errors, b9-continue specifically may stress the multi-section span case noted in the parked v0.5 work).

### 2026-05-03 — Build verification (autonomous loop)

- Re-ran `python3 build/build.py`. Output 499.4 KB (under 500 KB now; the new HTML/CSS work shaved off the Google Fonts payload).
- Idempotency confirmed: re-run produced byte-identical output (sha256 stable).
- Size profile of the 511 KB sample-build output:
  - HTML body: 484 KB (94.7%)
    - `<p>` tags across 2,235 paragraphs: 466 KB (91.2%)
    - Raw text content: 410 KB (80.1%)
    - HTML markup overhead: 74 KB (14.5%)
  - `<style>` blocks: 9.7 KB (1.9%)
  - `<script>` blocks: 17.5 KB (3.4%) — of which BRANCHES object: 2.7 KB (0.5%)
- **Final file projection** when all 23 branches lock: ~950 KB to 1 MB. Real branches add ~65,000 words ≈ ~360 KB additional text + ~80 KB markup overhead. The 500 KB advisory I gave earlier was wrong; the project's natural size with all branches is closer to 1 MB. Worth flagging to Rahul if he had a specific target in mind.
- All 10 canon beats parsed, 2,234 paragraphs spliced. 3 placeholder branches integrated. b1-walk correctly skipped (status `Pending Rahul`, not Locked).
- Reviews on b1-walk verified appended cleanly. Both PASS verdicts; voice has 2 minor FLAGs (tea-stall length, "forty years of one thing" near-repeat); arch zero FLAGs.

### 2026-05-03 — Post-b8-tell-lock maintenance review

Reviewed `process/voice-profile.md` and `process/architectural-threads.md` after b8-tell lock. The two additions made earlier (Tchaikovsky-overreach in §5; pre-emptive naming in §E.1) cover both b1-walk and b8-tell experiences. No further additions warranted — Beat 8 specific tics in §2 (bilingual bare, time-stamping, technical-as-character) all held in b8-tell drafting and were confirmed valid by review. b8-tell drafter's self-review accurately predicted both reviewer FLAGs, which is good calibration; if this pattern holds across more branches, may merit a §3 note on drafter self-review as quality signal.

### 2026-05-03 — Voice-profile + architectural-threads maintenance (post-b1-walk-lock)

Per `process/workflow.md` §7: maintenance triggered by b1-walk lock. Per workflow rule, maintenance lands when b1-walk is the first locked branch.

- `process/voice-profile.md` §5 — added two anti-patterns identified during b1-walk and b8-tell review:
  - Tchaikovsky-overreach in codas (b8-tell coda review).
  - Verbatim canon repetition without variation (b1-walk voice review).
- `process/architectural-threads.md` §E.1 — added the **pre-emptive naming of flagged risks** technique, after b1-walk demonstrated it. Drafters can address an architecturally flagged risk by writing prose that explicitly names the avoidance; reviewers credit when the prose does the work, not just claims to.

### 2026-05-03 — Test run (b1-walk integrated)

Static verification of `build/recognition-problem.html` (508.81 KB, 521,019 bytes). No browser available to this agent — the eight runtime checks below the line are deferred to a human/browser pass.

**Pass (static):**
1. **HTML parses cleanly.** Python `html.parser` reports 0 errors, 0 unclosed tags at EOF.
2. **Self-contained.** No `<link>` external stylesheets. No `<script src=...>`. No `@import url(...)`. No CDN host references (`cdn`, `googleapis`, `jsdelivr`, `unpkg`, `fonts.google` — all absent). Only `http://` reference is the SVG XML namespace `http://www.w3.org/2000/svg` (not a network fetch).
3. **b1-walk prose present.** All distinctive phrases located at expected counts: "He shows love in logistics" ×3 (canon mention + branch italic recall + summary), "kerosene lamp" ×1, "small unsponsored exchange" ×1, "tea stall" ×2, "swimming laps in a slow steady freestyle" ×1 (signature image), "what they had decided to keep" ×1 (closing hinge).
4. **BRANCHES JS object includes b1-walk.** Four entries present in BRANCHES: `b1-stub-coda`, `b1-stub-downstream`, `b1-stub-fork`, `b1-walk`. b1-walk entry has correct `id`, `name: "The Walk"`, full summary, `fork: { sectionId: "b1-s8", afterParagraph: "b1-s8-p12" }`, and a populated `paragraphs[]` array under `affects["b1-s8"]`.
5. **Marginal mark structure intact.** Canon `<p id="b1-s8-p12" class="fork-paragraph" data-fork="b1-walk">` carries an inline `<button class="branch-mark" data-branch="b1-walk" aria-label="A branch is available here">`. Each of the 4 branches has exactly one mark, one decision card, one fork-paragraph anchor, one post-fork container — consistent and 1:1.
6. **Decision card content wired.** `<div class="decision" id="decision-b1-walk">` contains the title "Branch · The Walk" and the full summary statically (not deferred to runtime). Commit/cancel buttons both present with `data-action` and `data-branch` attributes.
7. **Fork paragraph match.** `p#b1-s8-p12` text content equals the frontmatter `fork_at` exactly: `"You also said something I thought was interesting. You said he shows love in logistics. That it's the only language he has for it."` Canon side and BRANCHES splice metadata reference the same paragraph id.
8. **No coda for b1-walk.** The b1-walk BRANCHES entry contains no `branch-coda` class, no `<hr>`, no italic anomaly-log block. Last `paragraphs[]` element is the closing prose paragraph ending on "what they had decided to keep." Correct for Beat 1.
9. **No regressions on the 3 placeholder branches.** All three stubs still present in BRANCHES with their marks, decision cards, fork-paragraph anchors, and post-fork containers.
10. **File size.** 508.81 KB (522,562 bytes on disk; 521,019 bytes content). Up from 499.4 KB pre-b1-walk — a +9.4 KB delta for ~1,540 words of branch prose, consistent with the projected ~1 MB final size when all 23 branches lock.

**Browser-required tests deferred:**
- 60fps animation
- localStorage persistence across reload (the keyword is present 2× in the inlined JS, suggesting it's wired, but not exercised here)
- Decision card UX (mouse/keyboard)
- Cross-browser (Safari/Chrome)
- Reset returns to canon cleanly (the keyword "reset" is present 3× in the inlined JS, suggesting it's wired, but not exercised here)
- Page scroll-to-fork on selection
- One-branch-at-a-time enforcement at runtime
- Console errors / warnings on load

**Recommendation:** **Build can be locked at the static level.** Every static check passes — the integration is structurally sound, the splice is exact, and the file is genuinely self-contained. Final lock for the integration gate (quality-gates §2 last bullet, prototype-tester verification) requires the eight deferred runtime checks; those need a browser session and cannot be discharged from this agent. The structural artefact is ready for that browser pass, not blocking it.
