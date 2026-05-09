# Architecture v2 — Website rebuild

**Date:** 2026-05-08
**Supersedes:** `process/audit-html-css.md`, `audit-animation.md`, `audit-branch-logic.md`, `audit-build.md` (v1 audits, dated 2026-05-03) for delivery decisions only. Design decisions in those v1 audits — typography, marginal-mark style, decision-card shape, paper-temperature canon-vs-branch shading, split-flap mechanics — still apply unless explicitly superseded below.

This document is the working spec for W0–W5 of the website rebuild. It is short on purpose. Implementation details land in the code.

---

## 1. Delivery model

**Single self-contained HTML file → multi-page static website on GitHub Pages with a custom domain.**

The single-file constraint that drove most of v1's audits is gone. CSS and JS extract into separate files. Web fonts are now allowed. The site is a tree of pre-rendered HTML pages, each linked by clean paths.

### Build output

```
dist/
├── index.html                       — TOC / landing
├── beat-1/index.html                — Beat 1 canon
├── beat-1/walk/index.html           — Beat 1 with b1-walk auto-active on load
├── beat-1/repair/index.html
├── beat-1/carsick/index.html
├── …
├── beat-10/lie/index.html
├── making/index.html                — Making landing
├── making/conception/index.html
├── making/voice/index.html
├── making/agents/index.html
├── making/architecture/index.html
├── making/notes/index.html          — table of working docs
├── making/notes/bible/index.html
├── making/notes/ledger/index.html
├── making/notes/voice-profile/index.html
├── making/notes/threads/index.html
├── making/notes/workflow/index.html
├── 404.html                         — fallback
├── CNAME                            — GitHub Pages custom-domain marker
└── assets/
    ├── css/
    │   ├── base.css                 — typography, paper, layout
    │   ├── chapter.css              — beat page styles (split-flap, marks, cards)
    │   ├── making.css               — making-page styles (narrower column, no split-flap)
    │   └── animations.css           — keyframes, transitions, reduced-motion
    ├── js/
    │   ├── main.js                  — bootstrapping, routing helpers
    │   ├── branches.js              — commitBranch, returnToCanon, BRANCHES schema
    │   ├── splitflap.js             — flapParagraph, rewriteContainerParagraphs
    │   └── persistence.js           — localStorage state
    ├── fonts/                       — self-hosted woff2 (Newsreader, Plex Sans, Plex Mono)
    └── img/                         — favicon, OG image
```

### Per-beat pages, SPA-style branches within a beat

Each `dist/beat-N/index.html` contains the full canon prose for Beat N plus the BRANCHES JS object for that beat's branches. Branch interaction (split-flap rewrite, decision card, return-to-canon) is in-page — same mechanic as the v1 prototype, scoped to one chapter.

Between chapters, navigation is full page transitions (with the page-fade animation from §4). A reader on a Beat 3 branch who clicks Beat 5 in the TOC navigates to a new HTML page; localStorage carries forward branch state per beat.

This **resolves the multi-section runtime issue** that has been parked since 2026-05-07. Each page is its own canon — a branch in Beat 3 can't bleed into Beat 4 because Beat 4 is a different page.

### Deep-link auto-activation

URL `/beat-3/noriko/` loads `dist/beat-3/noriko/index.html` — a near-clone of `dist/beat-3/index.html` with a `<script>` tag that calls `commitBranch('b3-noriko')` after page load (or, equivalently, sets the localStorage active-branch key before script init runs). The split-flap then plays automatically on first paint of that URL.

Permalinks for branches are first-class. Sharing `/beat-3/noriko/` shares the experience of arriving at Beat 3 and being on Noriko's branch already.

---

## 2. Typography (locked)

**Direction A from the W0 plan, confirmed 2026-05-08:**

- **Body serif:** **Newsreader** (Production Type, free on Google Fonts, self-hosted woff2). Screen-optimised, designed for long reading, not overused.
- **UI / headings:** **IBM Plex Sans**. Technical-but-warm; pairs with Plex Mono.
- **System / coda register:** **IBM Plex Mono**. Used for the imprint, beat label, decision card chrome, codas, footer status.

Self-host all three faces (Latin subset + the few special chars in canon) under `assets/fonts/`. Preload the body Newsreader regular + italic to avoid FOUT on the prose.

### Type scale (provisional; tighten in W2)

| Element | Face | Size | Weight | Line height |
|---|---|---|---|---|
| Body prose | Newsreader | 1.05rem (~17.85px) | 400 / 400i | 1.7 |
| Beat title (H2) | Newsreader | 1.6rem | 300i | 1.2 |
| Section mark | Plex Mono | 0.78rem caps | 500 | 1 |
| Coda (italic block) | Newsreader | 0.95rem | 400i | 1.65 |
| Imprint / beat label | Plex Mono | 0.72rem caps tracked | 500 | 1 |
| Decision card title | Plex Mono | 0.78rem caps | 600 | 1.2 |
| Decision card summary | Newsreader | 0.95rem | 400i | 1.55 |
| Sidebar / TOC | Plex Sans | 0.86rem | 400 | 1.45 |

Paper `#f4f0e6`, ink `#1a1612`, branch ochre `#8b3a2e`, paper-deep `#ebe5d4`, paper-branch `#f2efe6`. Same palette as v1.

### Drop cap

Per-beat opener only (not per-section). Newsreader cap, 4 lines tall, ochre.

---

## 3. Routing & navigation

### URL structure

```
/                                — landing / TOC
/beat-1/  …  /beat-10/           — canon chapters
/beat-3/noriko/                  — chapter with branch auto-active
/making/                         — making landing
/making/conception/  /voice/  /agents/  /architecture/
/making/notes/                   — working-docs index
/making/notes/{bible,ledger,voice-profile,threads,workflow}/
/404.html                        — fallback
```

Branch slug in URL drops the `b{N}-` prefix (beat is already in path). The build verifies slug uniqueness within each beat.

### Sidebar / TOC

Carry over the v1 audit's Option B (drawer, hidden by default, persisted preference in localStorage). On the per-beat page, the drawer also includes the beat's section list and branch dots. On the TOC landing page, the sidebar is unnecessary — the page itself is the TOC.

### Header

Slim. Imprint left (mono caps), beat title centre, "Return to canon" right (visible only on a branch). The full chapter title and number sit in the article header, not in the page header.

---

## 4. Animations (provisional, browser-review at W3)

Carried over from the agreed palette:

- **Split-flap** (existing) — branch rewrite. Reduced-motion fallback: instant swap.
- **Branch-mark hover** — line scales 2.8em → 3.4em, label fades in. 200ms ease.
- **Decision card** — open from below with Y-offset (`translateY(8px)` → `0`) + fade. 280ms cubic-bezier.
- **Internal links** — left-to-right `text-decoration` draw using a pseudo-element underline; 240ms ease. Reduced-motion: static underline.
- **Page load stagger-reveal** — paragraphs fade in over 30ms cascade, capped at the first 8 paragraphs (rest snap in). Reduced-motion: no fade.
- **Scroll-to-fork on commit** — smooth scroll, fork paragraph briefly highlighted with a 1.2s background pulse in `--paper-deep`.
- **Page transitions between chapters** — fade-through-paper, ~250ms. Implemented via View Transitions API where supported; `opacity` fallback elsewhere.
- **Coda 11ms tick** — a tiny `11ms` glyph in Plex Mono ticks once in the bottom-right when a coda comes into view. Easter egg consistent with the chapter motif.

Hard rule: every animation respects `prefers-reduced-motion: reduce`.

---

## 5. Build pipeline (W1 spec)

### `build/build.py` rewrite scope

The existing `build/build.py` (1,466 lines) splices canon + branch markdown into a single self-contained HTML file. It needs to:

1. **Emit a directory tree** at `dist/` rather than one file at `build/recognition-problem.html`.
2. **Render templates** — `templates/base.html`, `templates/chapter.html`, `templates/making.html`, `templates/toc.html`. Use a small templating layer (Jinja2 if a dep is acceptable, or a simple `str.format`-based templater).
3. **Per-beat HTML** — for each beat, produce `dist/beat-N/index.html` (canon only) plus one variant per branch: `dist/beat-N/{branch-slug}/index.html`. The variant differs from the canon page only in a one-line bootstrap that auto-activates the branch.
4. **Splice logic preserved** — the BRANCHES JS object construction, fork-paragraph verification, paragraph IDs, branch coda placement: all carry over from v1.
5. **Render Making pages from a manifest** — `web/making-pages.yaml` lists the five essays + the curated working-docs notes. Each entry maps source markdown path → URL slug → page metadata. The build converts markdown → HTML against the making template.
6. **Copy assets** — fonts, CSS, JS, images, CNAME — into `dist/`.
7. **Emit 404.html** — a small fallback.

### Manifest format (for the Making section)

```yaml
# web/making-pages.yaml
essays:
  - slug: ""              # /making/
    title: "Making"
    source: web/making/index.md
  - slug: conception
    title: "How this was conceived"
    source: web/making/conception.md
  - slug: voice
    title: "On voice continuity"
    source: web/making/voice.md
  - slug: agents
    title: "The agent system"
    source: web/making/agents.md
  - slug: architecture
    title: "Architectural threads"
    source: web/making/architecture.md
notes:
  - slug: bible
    title: "Story bible v23"
    source: bible/bible-v23.md
  - slug: ledger
    title: "The ledger"
    source: ledger.md
  - slug: voice-profile
    title: "Voice profile"
    source: process/voice-profile.md
  - slug: threads
    title: "Architectural threads"
    source: process/architectural-threads.md
  - slug: workflow
    title: "Workflow"
    source: process/workflow.md
```

Source files for essays live in a new `web/making/` directory. Source files for notes are read directly from their existing locations (bible, ledger, process/) — the build renders them as HTML without modifying the source.

### Dev workflow

- `python3 build/build.py` — full build to `dist/`.
- `python3 build/build.py --watch` — incremental rebuild on file change. (Optional; deferred if it slows W1.)
- `python3 -m http.server 8000 --directory dist` — local serve for browser testing.

---

## 6. Hosting & deployment

### GitHub Pages with custom domain

- Repository on GitHub (existing or new — Rahul to confirm).
- `dist/` published from a `gh-pages` branch or via GitHub Actions on push to `main`.
- `CNAME` file in `dist/` carries the custom domain.
- DNS: Rahul configures the domain registrar; Apex `A` records to GitHub IPs + `www` `CNAME` to `<user>.github.io`.

### CI

A small GitHub Actions workflow:
1. Checkout main.
2. Set up Python 3.
3. Run `python3 build/build.py`.
4. Push `dist/` to `gh-pages` branch (or use the official `actions/deploy-pages` action).

This deploys on every merge to main. No manual step.

### Domain

Rahul to provide. Architecture is domain-agnostic; the only file affected is `dist/CNAME`.

---

## 7. Making section (W4 spec)

### Five essays

| Slug | Title | Author | Source approach |
|---|---|---|---|
| (root) | "Making" — overview | Rahul | Skeleton + extracts from `claude-code-opening.md`, `CLAUDE.md` |
| conception | "How this was conceived" | Rahul | Skeleton + extracts from `claude-code-opening.md` and the original directive |
| voice | "On voice continuity" | Rahul | Skeleton + extracts from `process/voice-profile.md` introduction |
| agents | "The agent system" | Rahul | Skeleton + extracts from `process/agent-roster.md`, `process/workflow.md` §1–2 |
| architecture | "Architectural threads" | Rahul | Skeleton + extracts from `process/architectural-threads.md` §A |

I prep a skeleton per essay (~300 words: section structure + relevant pull-quotes from existing project files). Rahul writes the prose. The essays are voice-of-the-author, not agent-drafted.

### Curated working docs

| Slug | Title | Source file |
|---|---|---|
| bible | Story bible v23 | `bible/bible-v23.md` |
| ledger | The ledger | `ledger.md` |
| voice-profile | Voice profile | `process/voice-profile.md` |
| threads | Architectural threads | `process/architectural-threads.md` |
| workflow | Workflow | `process/workflow.md` |

These are rendered as HTML against the Making template. They keep their existing markdown structure. Each gets a small header noting "this is a working document — not authored as a public-facing essay."

### Out by default (Rahul can override)

- Agent system prompts (`.claude/agents/*.md`)
- Per-branch drafting notes (in-process notes inside `branches/**/*.md`)
- `process/decisions.md`
- `STATUS.md` (live state; would mislead readers)
- Build code (`build/build.py`) — could be linked-out to GitHub instead

### Visual treatment

Same typography as fiction. Narrower column (28rem vs the fiction's 38rem — the prose is denser and benefits from a tighter measure). No split-flap. No marginal marks. A small mono header band — "MAKING / [ESSAY TITLE]" — distinguishes it from a beat page at a glance without changing the typographic register.

---

## 8. Acceptance criteria

The website is ready to deploy when:

- [ ] All 10 canon chapters render at `/beat-N/`.
- [ ] All 23 branches deep-link at `/beat-N/{slug}/` with the branch auto-active on load.
- [ ] Split-flap animation plays at 60fps on Chrome + Safari + Firefox.
- [ ] localStorage persists active branch per beat across navigation.
- [ ] The five Making essays render at their URLs.
- [ ] The five Making notes render at their URLs from their source markdown.
- [ ] All fonts self-host as woff2; no Google Fonts hot-link.
- [ ] `prefers-reduced-motion: reduce` disables split-flap and decoration animations.
- [ ] Mobile breakpoint (≤720px) holds at all paths.
- [ ] 404 fallback works.
- [ ] CNAME and DNS resolve to the custom domain.
- [ ] Rahul has signed off on the visual identity in browser.

---

## 9. What v1 audits still apply (read these for design context)

- `process/audit-html-css.md` — sidebar (drawer Option B), marginal mark style, canon-vs-branch shading (paper-temperature Option A), decision card design, branch signifiers (P1 + P2 + P4). All adopted.
- `process/audit-animation.md` — split-flap mechanics, frame budget, timing curves. Carry forward as-is for the rewrite animation.
- `process/audit-branch-logic.md` — BRANCHES schema, `commitBranch` / `returnToCanon` flow, decision-card markup. Carry forward; routing layer is added on top.
- `process/audit-build.md` — paragraph ID scheme, fork-paragraph verification, branch markdown front-matter contract. Carry forward.

The four v1 audits are not rewritten. They get a short header note pointing to this document for delivery decisions.

— end architecture v2 —
