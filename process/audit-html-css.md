# Audit — HTML & CSS for the Forest Edition

**Auditor:** `html-css-architect`
**Source:** `prototype/index-v4.html`
**Date:** 2026-05-03
**Status:** Audit + proposals only. **No code changed.** Implementation begins after Rahul approves.

This document is a read-and-decide artefact. Each section names what's there, what's right about it, what should change at scale (~140k words across 10 beats and 23 branches), and where there's a real tradeoff — gives Rahul two options.

---

## Preamble: scale shift

The prototype is a **single excerpt** (Beat 5, three sections, three branches). The real Forest Edition is **10 beats × ~14k words/beat × 23 branches**. Everything that feels fine at one-chapter scale needs re-examination at ten-chapter scale:

- A reader will spend hours, not minutes.
- Marginal marks will appear ~23 times across the read; they need to be felt as *structural* rather than as decorations specific to one passage.
- The TOC becomes load-bearing — at 140k words there is no scrolling-to-find.
- Canon-vs-branch shading must hold across many returns to canon and many branch choices.

The prototype was built well for an excerpt. The proposals below are about what changes when it stops being an excerpt.

---

## 1. Current typography

### What's there

- **Body face:** `Spectral` (Google Fonts), with `Georgia, serif` fallback.
- **Display & metadata face:** `JetBrains Mono` for the imprint, beat label, section marks, branch labels, decision-card chrome, footer status.
- **Sizing:** `html { font-size: 17px }`. Body paragraphs at `1.05rem` (~17.85px), `line-height: 1.75`.
- **Measure:** `--max-text: 38rem` (~646px at 17px base). Roughly 65–72 characters per line at the body size — within the 60–75 sweet spot.
- **Hierarchy:** drop cap on first paragraph of `#s1`; italicised display H1 in Spectral 300; small-caps-feeling beat label in mono.
- **Texture:** SVG noise overlay at 35% opacity, multiply blend; two soft radial gradients on the paper. This is the "old paper" feel.
- **Body weight 400, italic available; display H1 weight 300 italic.**

### What works

- The **measure is correct** for long-form. 38rem at 17px is in the right band for a reading-first text.
- **Spectral is a good choice**. It's a contemporary serif designed for screen reading at body sizes, with a quiet personality. Holds up at 17px on a Retina display, holds up at 17px on a 1080p ThinkPad.
- The **paper colour `#f4f0e6` against ink `#1a1612`** is a softened-warm pairing — high enough contrast for sustained reading, low enough that it doesn't burn. WCAG AAA at this measure.
- **Line height 1.75** is generous — appropriate for a literary work, *not* appropriate for technical prose. Right call.
- **Mono usage is disciplined.** Used only for chrome and metadata, not for prose. This is what gives the page its quiet authority.

### What to change for ~140k words

1. **External font loading is a hard-rule violation.** The prototype loads Spectral and JetBrains Mono from Google Fonts. The agent definition says: *"Single self-contained HTML file. CSS inlined. No external font loads unless inlined."* For a self-contained artifact, the fonts must either be (a) inlined as base64 woff2 (adds ~80–150KB, acceptable within the 180KB budget if we subset), (b) replaced with a reliable system stack, or (c) accepted as a deliberate exception. **This is a decision Rahul needs to make.** My recommendation: subset Spectral to Latin + the few special chars used, inline as woff2; replace JetBrains Mono with a system mono stack (`ui-monospace, "SF Mono", Menlo, Consolas, monospace`) since mono usage is small and chrome-only.

2. **The drop cap is scoped only to `#s1 p:first-of-type`.** That's correct for an excerpt but wrong for a book. At full scale we need a rule: drop cap on the first paragraph of *each beat*, not each section. The CSS becomes `article > section.beat:first-of-type p:first-of-type::first-letter` or — cleaner — a `.beat-opener` class controlled by the build step.

3. **No chapter / beat hierarchy yet.** The current page has H1 + section marks (i / ii / iii) only. A 10-beat book needs a Beat title (H2), section divider (the existing `i / ii / iii`), and possibly a sub-section break (a fleuron or asterism). Hierarchy proposal:
   - H1: the book title (only on cover/start).
   - H2 / `.beat-title`: italic Spectral 300, ~1.6rem, the beat title (e.g. "What the System Knows").
   - `.section-mark`: as exists.
   - `.flourish`: a centred ornament (three asterisks or a fleuron) for unmarked breaks within a section.

4. **Body size at 1.05rem may be marginally heavy at long-form.** I'd test 1.0rem (~17px) vs 1.05rem (~17.85px) with reading-mode line height. The current 1.05/1.75 is *just* on the comfortable side; 1.0/1.7 might read longer better. **Tradeoff:** larger text reduces eye strain per page but increases scrolling. For a book read in sessions, 1.05 is probably right. Worth one A/B with a real reader before locking.

5. **Italic body for in-prose emphasis is fine; italic for the entire `.note` block is on the edge.** Two paragraphs of italic at 0.92rem is a brief moment; if the same treatment ever wraps three+ paragraphs, switch to roman with a left-border accent.

6. **No print stylesheet.** A long-form work eventually needs one. Out of scope for v1 but flag for v2.

### Recommendation summary (typography)

- **Decide on font hosting.** Inline subset Spectral; system stack for mono. *Tradeoff: ~80KB of file weight vs offline-correctness and self-containment.*
- Generalise the drop cap rule to per-beat openers.
- Define the beat-level hierarchy (H2) before drafting beats 1–4.
- Hold body size at 1.05rem / line-height 1.75 unless a tester reports fatigue.

---

## 2. Current layout structure

### DOM hierarchy

```
body
  div.container (max-width 64rem, padding 4rem 2rem 8rem)
    header
      div.imprint
      h1
      div.beat-number
      button.return-to-canon (display:none until .branched)
    p.note
    article#article
      section.section#s1
        div.section-mark
        p (canon paragraphs)
        p.fork-paragraph[data-fork="b1"]
          button.branch-mark
        div.decision#decision-b1 (collapsed)
        div.post-fork[data-fork-target="b1"]
          p (canon continuation; gets rewritten on commit)
      section.section#s2 (same shape)
      section.section#s3 (same shape)
    footer
      div.branch-status
      div.system-note
    div.rewriting-pulse#pulse (fixed position, animation status)
```

### Rendering approach

- Pure CSS layout — no flexbox or grid for the page. The container is a centred block, the article is a centred max-width column, the marginal mark is positioned `absolute` to `right: -2.8rem` of the fork paragraph.
- The whole thing renders as one long scrolling column. No sidebar, no sticky chrome, no chapter nav. Scroll is the only navigation.
- Branch logic is JS-driven (split-flap rewrite via `flapParagraph` → `rewriteContainerParagraphs`).

### What works

- **Single-column-on-warm-paper is the right reading frame.** It is the digital analogue of a book page.
- **The article is the page; everything else is chrome.** The header is small. The footer is smaller. The reader is not asked to look at anything but the prose.
- **The `body.branched` class is a clean toggle** — branch-mode visual signaling currently flips a few colors via this single hook.

### What to change for the full Forest Edition

1. **No sidebar / no TOC.** The whole audit Rahul asked for is downstream of this gap. See §3.
2. **No beat boundaries in the DOM.** Currently `section.section` is used for `i`, `ii`, `iii` *within* beat 5. For 10 beats, we need a `section.beat` wrapper (one per chapter) containing `section.section` (the Roman-numeral subsections). The build step will produce this.
3. **`.post-fork` is a leaky abstraction.** It works for "the rewrite happens here" within a section, but it intermixes with paragraphs that *aren't* post-fork in adjacent beats. For the full book the cleaner shape is: every section's content lives inside a `.section-content` wrapper (the prototype already adds this lazily via `ensureSectionContentWrapper`), and branch rewrites act on the wrapper, not on a special `.post-fork` div. Worth making this the structural default rather than a fallback.
4. **The `.rewriting-pulse` fixed indicator is currently bottom-centre.** That's fine. With a left sidebar this position might compete with the sidebar or feel off-axis; might want top-right or in-sidebar status during animation. Coordinate with `animation-engineer`.
5. **`.container` max-width 64rem is wider than the article max-width 38rem.** Currently the spare horizontal real estate carries the marginal mark on the right. With a left sidebar TOC, that real estate gets consumed; the article centring needs a redesign (see §3).

### Recommendation summary (layout)

- Introduce `section.beat` wrappers and `.section-content` as the structural defaults at build time.
- Re-architect the page width to accommodate a left sidebar (§3) — this is the biggest structural change.

---

## 3. Left-sidebar TOC proposal

Rahul wants this. The constraint: **must not load before canon — canon stays the default reading experience.** I read this as: the sidebar must be available, but unobtrusive, and must not visually dominate the page on first paint. The reader's eye should land on the prose.

### Recommended structure

```
SIDEBAR
─────────
The Recognition Problem
Forest Edition

▾ Beat 1 — What It Remembers          [● ● ●]   (3 branches; visited dot)
    Section i
    Section ii
    Section iii

▾ Beat 2 — Fidelity                   [● ●]
    ...

▸ Beat 3 — What the Model Sees        [● ●]    (collapsed)

▾ Beat 5 — What the System Knows      [● · ●]  (middle branch is terminal)
    Section i
    ◉ Section ii    (current)
    Section iii
...

[Return to canon]   (when on a branch)
```

- **Beat-level entries** (10 of them) are the primary navigation.
- **Section sub-entries** appear under the currently-expanded beat only. Beats can be expanded/collapsed.
- **Branch indicators** appear next to each beat as a row of small dots — one per branch (2–3 per beat). A dot is filled if the reader has *visited* that branch in this session, hollow otherwise. The terminal-eligible branch (one currently — `b5-reset`) is given a slightly different shape (an open square or a half-fill) so its weight is felt, not announced.
- **Visited beats** get a subtle change to their entry — a tiny ochre underline or a 1-px ochre dot to the left of the beat title. Not a full strikethrough. *Felt rather than announced.*
- **Current section** is marked by a filled dot (◉) or a small ochre rule to the left.
- **The "Return to canon" button** lives in the sidebar when branched (currently it's in the header). The header version stays as a backup (one-click is one-click) but the sidebar is the canonical home for this control.

### Two options for placement & behaviour

#### Option A — Persistent thin sidebar (recommended)

A 14–16rem wide sidebar fixed to the left, always visible on viewports ≥ 900px. On smaller viewports it collapses to a hamburger that opens an overlay. The sidebar is **visually quiet** — same paper background, ink-faint text, a single 1px rule between sidebar and article column.

- **Pros:** chapter access is one glance away; no click required. The reader can orient at any moment. Visited / current state is constantly visible.
- **Cons:** consumes ~16rem of horizontal real estate. Article is centred in the remaining width. Some readers may find any visible chrome distracting.
- **Mitigations:** sidebar text is ink-faint (currently `#8a7d6a`), no bold, mono used only for the dot indicators. The sidebar can be hidden with a tiny `‹` button if the reader wants pure prose.

#### Option B — Drawer sidebar (collapsible, hidden by default)

Same content as Option A, but **closed by default**. A small `≡` icon in the top-left corner (or a `‹‹` tab on the left edge) opens it. Once opened, it can stick or auto-close on chapter selection.

- **Pros:** canon really *is* the default — sidebar is opt-in. The page on first load looks identical to the current prototype.
- **Cons:** chapter navigation requires a click first. Returning to canon from a branch requires more eye-travel (the "Return to canon" header button still works, so this isn't a blocker).
- **Mitigations:** remember user preference in localStorage; if reader opens sidebar once, keep it open thereafter.

**Tradeoff to decide:**

> *Option A* favours navigability and orientation. *Option B* favours immersion and respects the "canon stays the default reading experience" constraint more literally.

My recommendation is **Option B** for v1, with state persisted in localStorage so a reader who opens it once gets it on subsequent visits. This honours the "canon-first" rule, gives the reader full agency over chrome, and matches the existing aesthetic (header is currently small and centred — a quiet drawer matches that register better than a permanent sidebar).

### Visited / selected indication

- **Visited chapter:** a small ochre dot (`var(--branch)`) to the left of the beat title. Subtle — same ochre family as the marginal mark.
- **Current chapter:** ochre 2px left rule (using border-left), no fill change.
- **Branched in this session:** the branch's dot among the row of branch dots is filled ochre; if it's the active branch, also outlined.
- **Terminal-eligible branches:** square dot rather than round dot. The shape difference is just-perceptible; a reader will likely notice across multiple beats but won't be told what it means until they pick one.

### Constraint compliance

- Canon stays the default: Option B keeps the sidebar closed on first load.
- Returning to canon is one click away: button in header (already exists) AND in sidebar (when open).
- One branch at a time: sidebar reflects the active branch with a unique mark; choosing another from the sidebar would route through the same `commitBranch` flow.

---

## 4. Marginal mark style — current and refinements

### Current

```css
.branch-mark::before {
  content: ""; display: block;
  width: 1px; height: 2.8em;
  background: var(--branch);  /* #8b3a2e — ochre/oxblood */
  transition: width 0.3s ease, height 0.3s ease;
}
.branch-mark:hover::before, .branch-mark:focus::before {
  width: 2px; height: 3.4em;
}
.branch-mark .label {
  /* "branch" appears on hover, in mono caps */
  opacity: 0; → 1;
}
```

- Position: `right: -2.8rem` of the fork paragraph (so the mark sits in the right margin).
- Mobile: flips to `left: -1.6rem` at ≤720px.
- Branched state: all marks fade to `opacity: 0.25` and become `pointer-events: none`. The active branch's mark is hidden entirely.

### What works

- **The line is thin enough to be unobtrusive but coloured enough to be unmistakable.** Ochre against warm paper reads as "an editor's pencil mark in the margin." Right vocabulary.
- **The hover-grow + label-fade combo** is restrained and readable. The label "branch" in mono caps tells the reader exactly what they're being offered without spelling it out as a button.
- **Branched-state dimming** is the right behaviour: when you're on a branch, the other forks are *visible but muted* — like recognising you took a different path.

### Refinements needed for 23 branches

1. **Some marks need to indicate "this branch is terminal-eligible" without saying so.** Per `ledger.md` §2.5, terminal-eligible branches should not announce themselves. But there should be a felt difference — a reader who has chosen several branches across the read should sense that some carry more weight than others. **Proposal:** terminal-eligible marks get a slightly longer line (3.6em vs 2.8em) or a tiny serif at top and bottom (like a tiny capital-I bracket). The difference is sub-articulate. This is a Rahul call.

2. **The tap target on mobile (1.2rem wide) is below the WCAG-recommended 44×44px.** Increase to 2rem on mobile; the visible 1px line stays the same, only the click area widens.

3. **A reader returning to a beat where they already chose a branch should see** *something* differentiating that mark from an unvisited one. Currently localStorage stores only the current `state.branch`. Proposal: extend state to track `visitedBranches: []`; visited marks get filled circles at their tip (like a thumbtack). Subtle. Optional via a "show my history" toggle if Rahul wants to keep the page maximally clean for re-reads.

4. **Currently there's no positional collision check.** With 23 branches across 10 beats and ledger §2.2's "well-separated fork points" rule (≥20% chapter separation), collisions are unlikely. But the mark's `top: 0.45rem` is paragraph-relative — if two fork paragraphs are close enough, two marks could overlap. Worth a unit test from `prototype-tester`.

5. **Animation budget.** The hover transition is 0.3s width+height. Across a long-form read this fires every time a reader's mouse drifts past a mark. Consider reducing to 0.2s or restricting to keyboard focus only. Minor.

6. **Reduced motion.** No `@media (prefers-reduced-motion)` rules anywhere in the prototype. Add one that drops the hover-grow transition (and, separately, governs the split-flap animation — that's `animation-engineer`'s call).

### Recommendation summary (marginal mark)

- Accept the current line as the canonical fork indicator.
- **Decide on the terminal-eligible visual differentiation** (longer line vs none) — Rahul call.
- Widen mobile tap target.
- Add "visited" indication if we agree with the design, gated on a setting.
- Add `prefers-reduced-motion` handling.

---

## 5. Canon-vs-branch shading proposal (NOT YET IMPLEMENTED)

This is the big one. The reader needs to know — at a glance, without having to look at the footer or read a label — whether they are on canon or in a branch. *Subtle, not loud.* *Felt rather than announced.*

The prototype currently signals branch state via:
- A footer text change: `Reading: Branch · The Fourth Opinion`.
- `body.branched .imprint { color: var(--branch); }` and `body.branched .beat-number { color: var(--branch); }` — i.e., the small mono labels at the top change colour.
- The "Return to canon" button appears.

That's all. The **prose itself doesn't change visually** when on a branch. A reader scrolling through paragraphs has no peripheral cue.

### Two options for canon-vs-branch shading

#### Option A — Paper temperature shift (recommended)

When on a branch, the paper colour shifts ~3% cooler/greener (`#f4f0e6` → `#f1eee5` or `#f2efe6`). The shift is below the threshold of conscious noticing on its own, but the reader *senses* the page is different. Combine with:

- Marginal-rule colour for the branched section: a **2px ochre rule** appears to the left of the rewritten paragraphs (the post-fork div). Indicates "this is the part that changed." Disappears on return to canon.
- Footer status change (already exists).
- Beat-number colour change (already exists).

The total effect: paper feels half a degree cooler; the rewritten passages carry a quiet ochre rule on the left. The reader knows *they are in a different version* and *which paragraphs are the difference*.

- **Pros:** non-invasive, retains the warm-paper aesthetic, easy to implement (CSS variable swap on `body.branched`). The left rule on rewritten paragraphs is structurally informative — it tells the reader *the change starts here*.
- **Cons:** the paper-shift is so subtle some readers won't perceive it consciously. The signaling load falls on the left rule and the chrome.
- **Mitigations:** the chrome already says "branch"; this is reinforcement, not the only signal.

#### Option B — Italic eye thread

When on a branch, every rewritten paragraph (the ones the split-flap re-rendered) is **rendered in a slightly thinner italic** (or in a slightly lighter ink colour, e.g., `--ink` → `--ink-soft`). The unmodified canonical paragraphs around it stay roman / full ink. The visual is: *a branch passage reads like a quotation, slightly italicised, the reader's eye recognises it as the alternate.*

- **Pros:** strongly felt at the prose level. The reader sees the difference inside the words, not in the chrome. "What's italicised has been rewritten."
- **Cons:** italics-as-branch interferes with italics-as-emphasis. The Forest text uses italics liberally for emphasis (foreign words, internal thought, titles). Doubling up the typographic load is risky. This option also makes a branch *visually loud* in a way that violates "subtle, not loud."
- **Mitigations:** none clean. This option fails the brief unless we redefine what "subtle" means.

**Tradeoff:**

> *Option A* satisfies "felt rather than announced." *Option B* satisfies "knows they are on a branch" but at the cost of subtlety and a typographic conflict.

**Recommendation: Option A.** Paper-temperature shift + 2px ochre left rule on rewritten paragraphs + existing chrome changes. Three quiet signals together that don't shout but together produce unambiguous awareness.

### Implementation sketch (for later)

```css
:root {
  --paper: #f4f0e6;
  --paper-branch: #f2efe6;     /* ~3% cooler */
  ...
}

body.branched { background: var(--paper-branch); }
body.branched .post-fork {
  border-left: 2px solid var(--branch);
  padding-left: 1.2rem;
  margin-left: -1.2rem;        /* keep the text column constant */
}
```

The `body.branched` paper transition should ride a `transition: background 1.2s ease` so the change happens during the split-flap rewrite, not before — the **paper itself rewrites along with the text**. That's a small detail with a large feel.

---

## 6. Decision card design

### Current

```css
.decision { max-height: 0; overflow: hidden; transition: ...; }
.decision.open { max-height: 400px; margin: 1.4rem 0 1.6rem; }
.decision-inner {
  background: var(--paper-deep);
  border-left: 2px solid var(--branch);
  padding: 1.4rem 1.6rem;
}
```

- Card slides open inline below the fork paragraph when the marginal mark is clicked.
- Contains: title in mono caps with ochre, italic summary, two buttons ("Follow this branch" primary ochre, "Stay with canon" secondary ink).
- Uses `--paper-deep` (`#ebe5d4`) — slightly darker than the page paper. Reads as "an inset card on the page" rather than a modal.

### What works

- **Inline placement** is correct. A modal would feel like an interruption; the inline card feels like the book is offering a choice in place. Matches the "the book is talking to you" voice.
- **The two buttons are equally weighted** (same size), but the primary action is the branch and the secondary is staying. This is right. The decision should be felt as "do you want to step off the path" — both options are real.
- **The italic summary** is voiced as a question/proposition, in the same register as the prose. Good.
- **`--paper-deep` background** does the work — the card is felt as a different surface without becoming a different colour family.

### Refinements

1. **The 400px max-height** is a magic number. Some branches will have longer summaries (especially if we add a "what changes" preview). Use `max-height: 24rem` and let summary length flex. Or switch to a CSS Grid trick for true auto-height transition.

2. **The card stays open until the reader clicks "Stay with canon" or commits.** What if the reader scrolls away? Current behaviour: card stays open, branch-mark stays visible. Proposal: scroll-out closes the card silently (still scroll-back-and-it's-open if the reader returns, since state is in DOM). Minor UX nicety.

3. **Animation timing.** `max-height` transitions are notoriously expensive at full document size. With one card open, fine. With `transition` duration 0.45s and a 400px target, this is not a perf concern — but flag for `animation-engineer` if we ever animate multiple cards or longer cards.

4. **A "preview" affordance.** Currently the card says only the branch title and a one-sentence summary. A reader might want a peek at what changes — *not* a full preview (that would foreclose the surprise of the rewrite), but maybe the first few words of the divergent paragraph faded in. Risky; could break the magic. **Decision for Rahul.** Default: don't add it.

5. **The card has only two buttons.** No "tell me more" or "save for later." Good. Don't add a third option. (For terminal-eligible branches we may want a tiny "this choice carries weight" microcopy in the summary itself, voiced in-character. Not chrome.)

6. **Decision card's title is currently `Branch · The Fourth Opinion`.** The bullet separator with mono caps gives it weight. For 23 branches, the convention should be: every card title follows `Branch · [Branch Name]`. Already the case; lock it in via build template.

### Recommendation summary (decision card)

- Keep the design. It's correct.
- Make max-height fluid.
- Auto-close on scroll-out.
- Do **not** add preview microcopy unless Rahul wants it.

---

## 7. Branch signifiers — proposals

Rahul: *"Better signifiers for branches."* The marginal mark is the canonical fork indicator. *"Improve as needed without losing its unobtrusiveness."*

### Reading the room

The marginal mark is doing one specific job: *announcing a fork is available at this paragraph*. It is not (yet) doing:

- Indicating **what kind** of branch (local vs terminal-eligible).
- Indicating whether the reader has **already explored** this branch.
- Indicating whether the branch is **currently active** (well — it is, by hiding itself when active. But that's all.).
- Indicating the branch's **scope** (does it rewrite three paragraphs or three sections?).

These are four different signals the reader could benefit from, with very different priorities.

### Proposals (composable — Rahul picks 0, 1, 2, 3, or all)

**P1 — Terminal-eligible mark differentiation (high value).**
Terminal-eligible branches get a longer line (3.6em vs 2.8em) OR a tiny perpendicular cap at the top. The reader senses, after hitting one or two, that some marks weigh more. They never get told why. Aligns with ledger §2.5 (bend, don't break).

**P2 — Visited-branch indication (medium value).**
A 3px ochre dot at the bottom of the marginal line, fill = visited. Persists across sessions via localStorage. Lets a re-reader navigate by what they've seen.

**P3 — Scope indication (low value, possibly noisy).**
The line's height as scope: 2em for "rewrites this paragraph and the next," 4em for "rewrites the rest of the chapter," 6em for "rewrites this chapter and downstream." Gives the reader a felt sense of *how much will change*. **Risk:** announces too much before the reader commits, foreclosing the surprise. Probably violates the spirit of the brief. Listed for completeness; recommend against.

**P4 — Branch density indication in the TOC (high value).**
Each beat in the sidebar shows N dots = N branches. Already proposed in §3. This is the macro-signifier complement to the marginal mark's micro-signifier. The reader knows from the TOC "Beat 5 has three forks; Beat 1 has three forks; Beat 9 has two." Sets reading expectations.

**P5 — A whisper-quiet hover preview (medium-low value).**
On hover, beneath the existing "branch" label, a 4-word fragment of the branch's title fades in: *"What if she'd asked the lab"* — the question the branch poses. Currently the title only appears in the decision card; this would let a reader survey forks without committing to opening cards. **Risk:** turns the marginal mark into a button-with-a-tooltip, which it currently is not. The mark is a signal, not a summary.

**P6 — A small numeric or alphabetic glyph next to the mark (low value).**
A tiny mono `b1`, `b2` etc. at hover. Currently there's no such labeling. Tradeoff: adds chrome. Probably skip.

### Recommendation

- **Adopt P1** (terminal-eligible differentiation). Quiet, on-brand, structurally meaningful.
- **Adopt P2** (visited indication) IF we agree on the localStorage extension; it's a re-reader feature that doesn't intrude on first reads.
- **Adopt P4** (TOC branch density dots). Already in the §3 proposal. Locks in.
- **Skip P3, P5, P6.** Each adds noise or commits the chrome to doing too much work.

---

## Summary of decisions for Rahul

In rough priority order:

1. **Font hosting** — inline-subset Spectral or accept system stack? *(blocks self-containment compliance)*
2. **Sidebar Option A vs B** — persistent-thin vs drawer? *(my rec: B)*
3. **Canon-vs-branch shading Option A vs B** — paper-temperature + left rule, or italic re-rendering? *(my rec: A)*
4. **Marginal mark P1** — adopt terminal-eligible differentiation? *(my rec: yes, longer line)*
5. **Marginal mark P2** — adopt visited indication? *(my rec: yes, optional toggle)*
6. **Beat-level structural hierarchy** — confirm `section.beat` + H2 `.beat-title` + per-beat drop cap? *(my rec: yes)*
7. **Decision-card refinements** — fluid max-height, auto-close on scroll? *(my rec: yes)*

Once Rahul decides, I implement against `build/recognition-problem.html` (the build target), coordinating with `build-engineer` on templates, `animation-engineer` on the split-flap hooks, and `branch-logic-engineer` on decision-card markup.

— end audit —
