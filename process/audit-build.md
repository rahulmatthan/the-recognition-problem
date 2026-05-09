# Audit + Build Plan — `build/build.py` v0

**Author:** build-engineer
**Date:** 2026-05-03
**Scope:** Audit the existing `prototype/index-v4.html`, then propose a build pipeline that produces the Forest Edition (`build/recognition-problem.html`) from `canon/*.md` plus locked branch markdown.

---

## 1. Current state of `prototype/index-v4.html`

### Build infrastructure: none.

`prototype/index-v4.html` is a **hand-authored, fully self-contained HTML file**. It has:

- Inline `<style>` block (lines 10–287) — all CSS is in-file. Custom properties at `:root` define the paper / ink / branch palette.
- One **external** dependency: Google Fonts (`Spectral` + `JetBrains Mono`) via `<link rel="stylesheet">` at lines 7–9. This violates the "no external font loads" rule from `quality-gates.md` §3 and `ledger.md` §1.2 — the build will need to fix it.
- Inline `<script>` block (lines 424–1013). All JS in-file. No bundler, no CDN.
- No build step; the file works as-is when opened in a browser. No `build/` artifacts exist (the `build/` directory is empty).

### Canon: embedded directly as HTML.

The canon prose for Beat 5 (sections i, ii, iii — three sample sections, not the full beat) is **hand-authored as HTML** inline in the `<article>` (lines 308–413). Each section is a `<section class="section" id="sN">` containing a `<div class="section-mark">`, `<p>` paragraphs, an inline `<p class="fork-paragraph" data-fork="bN">…</p>`, a `<div class="decision">…</div>` card, and a `<div class="post-fork" data-fork-target="bN">…</div>` block holding the canon-side post-fork prose.

There is no markdown source for this prototype. The HTML *is* the source.

### Approach / language:

Vanilla JS, vanilla CSS, no framework. The animation logic (split-flap, lines 519–715) is custom: it pads old/new text to equal length, character-tile spans get random flap chars then settle, with cascading paragraph overlap (`PARAGRAPH_OVERLAP = 0.55`). Diff-aware: `normalizeHTML()` + `hasAnyChange()` short-circuit unchanged paragraphs.

This animation engine is **the asset to preserve.** The build script must not break its DOM contract.

---

## 2. Current branch handling

Branches in `prototype/index-v4.html` are **hardcoded as a JS literal**, not driven by markdown. The `BRANCHES` object (lines 428–490) holds three sample branches (`b1`, `b2`, `b3`) for Beat 5 demo only:

```js
const BRANCHES = {
  b1: {
    name: "The Fourth Opinion",
    section: "s1",
    s1_replacement: [ "<p>...</p>", ... ],   // array of inner-HTML strings
    downstream: [ { section: "s2", paragraphs: [...] }, ... ]
  },
  ...
};
```

Properties:

- `name` — display name shown in header / status / decision card.
- `section` — fork section ID (`s1`/`s2`/`s3`).
- `<sectionId>_replacement` — array of paragraph-HTML strings replacing the *post-fork* content of the fork section.
- `downstream` — array of `{section, paragraphs[]}` objects for sections after the fork that the branch also affects.

**Missing fields** (vs. `ledger.md` §8.5 spec): no `id` (the key serves as id), no `summary` separate from the decision card, no structured `fork: {sectionId, afterParagraph}`, no `affects: { sectionId: { fromParagraph, paragraphs[] } }`. The build script will reshape the JS object to the spec.

The fork-paragraph contract is *implicit* in the prototype: the fork text lives only in the canon HTML; the branch JS just declares which section it forks in. No verification anywhere.

---

## 3. `build.py` v0 — design

### 3.1 Inputs

```
canon/                           # all 10 chapters
├── beat1-draft-v7.md
├── beat2-draft-v8.md
└── …

branches/                        # locked branches only
├── beat1/
│   ├── b1-walk.md                # status: Locked
│   └── …
└── …

prototype/index-v4.html          # template / shell
process/branch-template.md       # for parsing reference
```

The build reads every `canon/*.md` and every `branches/**/*.md` whose frontmatter has `status: Locked` (case-insensitive on the value, exact on the key). Drafts and in-review branches are skipped silently with an info-line: `skipping b1-walk.md (status: Draft v2)`.

### 3.2 Output

`build/recognition-problem.html` — a single, self-contained file. No CDN, no Google Fonts link, all CSS/JS inlined. Idempotent.

### 3.3 Dependencies & runtime

Python 3.11+. Standard library plus **two** third-party libraries:

- **`mistune` (3.x)** for markdown parsing.
- **`PyYAML`** for frontmatter parsing.

Pinned in `build/requirements.txt`. Build script callable as `python3 build/build.py` from repo root.

### 3.4 Markdown parser choice — `mistune`

**Decision: use `mistune` 3.x with a custom renderer subclass.**

Considered:
- `markdown` (Python-Markdown) — mature but extension API is awkward; conversion of italics/em is fine but custom block hooks are verbose.
- `mistune` 3 — fast, AST-first, easy to subclass `HTMLRenderer`. Best fit.
- Custom regex parser — too brittle. Rejected.

Reasons mistune wins:

1. **Italic codas:** the canon and branch markdown use `*…*` for the Tchaikovsky-register coda paragraphs. Mistune emits these as `<em>…</em>`. The build wraps any *paragraph that is wholly italic and is the last paragraph of a section* in `<p class="branch-coda-line">…</p>` to match the prototype's coda styling (lines 226–235 of `index-v4.html`). A renderer hook does this cleanly.
2. **Section breaks:** the canon uses `---` (horizontal rules) to separate sections. Mistune emits `<hr/>`. The renderer collects paragraphs *between* hrs into `<section class="section" id="sN">` blocks with auto-incrementing numerals.
3. **Frontmatter:** mistune does not parse YAML frontmatter. The build strips frontmatter (between the first two `^---$` lines) before handing the body to mistune; YAML is parsed separately with `PyYAML`.
4. **Inline `<em>`:** mistune emits `<em>` from `*foo*`. We preserve as-is — the prototype's CSS already styles `em`.

### 3.5 Canon parsing

For each `canon/beatN-draft-vM.md`:

1. Strip frontmatter (none expected on canon, but tolerate it).
2. Render to HTML via mistune.
3. Walk the rendered tree (or re-parse with `html.parser` from stdlib): split on `<hr>`. Each segment becomes a `<section class="section" id="bN-sK">` (where `K` is an auto-incrementing index per beat starting at 1, and `bN` indicates the beat). The first H1 (`# What It Remembers`) becomes the chapter title. The H3 line (`### Beat 1 — The Memory People Asked For`) becomes the chapter subtitle. The `*2027*` line becomes a small dateline.
4. Each section gets a `<div class="section-mark">i</div>` (Roman numerals i, ii, iii, …) — preserving the prototype's visual rhythm.
5. Each `<p>` gets a stable id: `bN-sK-pJ`. This is what `fork_at` resolves against.

**Canon output is wrapped in a single `<article>`** with the same structure the prototype expects: outer container, header, note, article, footer.

### 3.6 Branch parsing

For each `branches/beatN/<id>.md`:

1. Parse frontmatter with PyYAML. Required keys per `branch-template.md`: `id`, `beat`, `title`, `fork_at`, `type`, `length_target`, `status`. Skip branches whose `status` is not exactly `Locked`.
2. Parse markdown body with mistune. Skip everything before the `## Branch prose` heading. Skip everything from `## Drafting notes` onward.
3. Within `## Branch prose`, split paragraphs by `<hr>`. The expected structure is **`prose paragraphs` → `<hr>` → `*coda*` → `<hr>`** (the branch template's three-dash separator before/after the coda). Beat 1 and Beat 7 branches do not have codas; the build does not require one.
4. Each branch prose paragraph becomes a `<p>` (or `<p class="branch-coda-line">` for the italic coda).

### 3.7 Fork-paragraph contract — the non-negotiable check

The frontmatter `fork_at` field must match the canon paragraph **character-for-character** (after both have been normalised: trim leading/trailing whitespace, collapse internal runs of whitespace to single spaces, leave punctuation untouched, leave Unicode untouched — em-dashes, curly quotes, accents are all preserved as-is).

Algorithm:

```python
def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip())

for branch in locked_branches:
    fork_text = normalize(branch.frontmatter["fork_at"])
    canon_paras = canon_paragraphs_for_beat(branch.frontmatter["beat"])
    matches = [p for p in canon_paras if normalize(p.text) == fork_text]
    if len(matches) == 0:
        die_with_diff(branch, fork_text, canon_paras)
    if len(matches) > 1:
        die_ambiguous(branch, matches)
    branch.fork_paragraph_id = matches[0].id   # bN-sK-pJ
```

**On mismatch the build fails — exit code 1 — with this format:**

```
ERROR: branches/beat1/b1-walk.md fork_at does not match canon.

  branch:  branches/beat1/b1-walk.md  (line 4 of frontmatter)
  canon:   canon/beat1-draft-v7.md

  Expected (from branch frontmatter):
    She walked along the road, the sea on her left, the road dust on
    her right, and let the argument settle into her body like weather.

  Closest canon match (canon/beat1-draft-v7.md, line 235):
    She walked to the beach. The sand was bright and the sea was loud
    and she found a spot in the shade of a catamaran hull and sat with
    her knees pulled up and her phone in her hand and the particular
    loneliness of being angry with someone you love.

  First differing character: position 12.
  expected ch:  'a' (U+0061)
  canon    ch:  't' (U+0074)

Fix: copy the canon paragraph verbatim into the branch's fork_at field.
The build refuses to splice on mismatch — a wrong fork paragraph
corrupts the splice and is non-negotiable.
```

The "closest canon match" is computed via `difflib.get_close_matches` against the normalized canon paragraphs of the same beat. Showing the closest neighbour saves drafters minutes of squinting.

### 3.8 Splice mechanism

Once `fork_paragraph_id` is resolved (e.g. `b1-s7-p3`), the build:

1. Locates the section containing the fork paragraph (`b1-s7`).
2. Wraps the fork paragraph: adds `class="fork-paragraph"`, sets `data-fork="<branch-id>"`, appends an inline `<button class="branch-mark" data-branch="<id>" aria-label="A branch is available here"><span class="label">branch</span></button>`.
3. Inserts the decision card `<div class="decision" id="decision-<id>">…</div>` immediately after the fork paragraph. The card's `decision-summary` is taken from a new optional frontmatter key `summary:` if present, otherwise auto-generated as `"What if [title]?"` (pending `branch-drafter` providing summaries explicitly — surfaced as a v0.5 follow-up).
4. Inserts a `<div class="post-fork" data-fork-target="<id>" data-section="<sectionId>">…canon paragraphs from p+1 to end of section…</div>` after the decision card. This block holds the canon's post-fork content (so canon reads cleanly when no branch is selected).
5. The remaining canon paragraphs of that section (after the fork) are *moved* into the post-fork div — they no longer appear as section-direct children. This matches the prototype's structure (lines 340–342, 372–374, 406–410).

### 3.9 BRANCHES object population

After all branches are spliced, the build emits a JS object literal:

```js
const BRANCHES = {
  "b1-walk": {
    id: "b1-walk",
    name: "The Walk",
    summary: "What if Meera had walked the road instead of the beach? …",
    fork: { sectionId: "b1-s7", afterParagraph: "b1-s7-p3" },
    affects: {
      "b1-s7": {
        fromParagraph: "b1-s7-p4",      // first paragraph after fork
        paragraphs: [ "<p>…</p>", "<p>…</p>", … ]
      },
      "b1-s8": {
        fromParagraph: "b1-s8-p1",
        paragraphs: [ "<p class=\"branch-coda-line\"><em>…</em></p>" ]
      }
    }
  },
  …
};
```

The shape exactly matches `ledger.md` §8.5. The animation engine in the prototype consumes a slightly different shape (`s1_replacement`, `downstream`); the build emits the new shape and a small adapter at the top of the JS adapts the engine's lookups (`getReplacementForSection`) to read from `affects[sectionId].paragraphs`. This is a 10-line change, not a rewrite of the animation.

### 3.10 Marginal-mark insertion

Step 3.8.2 inserts the `<button class="branch-mark">` inline at fork paragraphs. CSS in the prototype handles positioning via `.fork-paragraph` + absolute-positioned `.branch-mark`. No additional CSS work needed for v0.

If two branches fork at the same canon paragraph (per the ledger this is allowed for some beats), the build appends multiple `branch-mark` buttons inside the same `.fork-paragraph`. CSS will need a small tweak to space them; flagged for v0.5.

### 3.11 CSS / JS / fonts inlining

- **CSS:** copy the prototype's `<style>` block verbatim into the output. Already inline.
- **JS:** copy the prototype's `<script>` block, with the `BRANCHES` literal swapped for the build-generated literal and the small adapter for the new object shape.
- **Fonts:** *replace* the Google Fonts `<link>` with **system-font fallbacks for v0**. The prototype's `font-family: 'Spectral', Georgia, serif` already falls back gracefully — the rendered output will use Georgia / system serif. We accept this for v0; subscribing-grade Spectral inlining (base64-embedded WOFF2, ~120kb per weight) is a v0.5 task. **Decision flagged for Rahul:** acceptable to ship v0 with system fonts (Georgia / SF Mono), or do we inline Spectral now? See §5 risks.

### 3.12 Idempotency

Same inputs → byte-identical output. To guarantee:

- File listings are sorted (lexicographic) before processing.
- The BRANCHES object literal is emitted with sorted keys.
- Section IDs, paragraph IDs are deterministic (beat number + section index + paragraph index).
- No timestamps in the output. No build-id. No `<!-- generated 2026-05-03 -->` comment unless explicitly requested.
- A final SHA-256 of the output is printed at the end of the build for quick diffing.

Idempotency is testable: `make build && cp build/recognition-problem.html /tmp/a && make build && diff /tmp/a build/recognition-problem.html` must produce no output.

---

## 4. Placeholder branch strategy (W1 unblocker)

Real branches won't lock until W2+. To make the build runnable end-to-end during W1, the build-engineer ships **stub branches** in `branches/beat1/` with `status: Locked` and minimal but real prose. Three stubs are enough to exercise the splice mechanism: one fork in early-section, one in mid-section, one with a downstream effect on a later section.

### Placeholder file: `branches/beat1/b1-stub-walk.md`

```markdown
---
id: b1-stub-walk
beat: 1
title: The Walk (placeholder)
fork_at: |
  She walked to the beach. The sand was bright and the sea was loud and she found a spot in the shade of a catamaran hull and sat with her knees pulled up and her phone in her hand and the particular loneliness of being angry with someone you love.
type: Local
length_target: ~1500 words
status: Locked
summary: Build-pipeline placeholder. Real prose pending b1-walk lock.
---

# Branch: The Walk (placeholder)

## Branch prose

She walked the road instead. The road was dust and the dust was hot and her sandals filled with it within thirty seconds, and she did not turn around. *(Placeholder paragraph — will be replaced when b1-walk locks.)*

The road carried tuk-tuks and stray dogs and women with umbrellas against the sun, and Meera among them, walking. *(Placeholder.)*

She did not call Maya. *(Placeholder.)*

---

*Placeholder coda. The real coda will be written by `branch-drafter` when b1-walk drafts.*

---

## Drafting notes

Placeholder for build-pipeline verification only. Replace this entire file when b1-walk locks. The `fork_at` paragraph is taken from `canon/beat1-draft-v7.md`, line 235.

## Self-review

N/A — placeholder.

## Review log

- 2026-05-03 build-engineer: placeholder created so build.py v0 runs end-to-end. Replace before locking real b1-walk.
```

### Placeholder fingerprint

Every placeholder branch has `id` ending in `-stub-` (so `branch-drafter` and orchestrator can recognise them) and a banner comment in the prose. The build emits a console warning per placeholder: `WARN: integrating placeholder branch b1-stub-walk; replace before final lock.` This warning is by design — it nags until placeholders are replaced.

### Three placeholders for W1

1. `b1-stub-walk` — fork in late section, no downstream effects.
2. `b1-stub-carsick` — fork mid-chapter, one downstream paragraph in next section.
3. `b1-stub-repair` — fork late, italic-coda only (single paragraph downstream).

These three exercise: (a) basic fork + splice, (b) downstream propagation, (c) coda-only branches. Together they cover every code path in the build.

When the real `b1-walk`, `b1-carsick`, `b1-repair` lock, the orchestrator deletes the corresponding `-stub-` files in the same commit that adds the real ones. The build's `WARN` count drops to zero.

---

## 5. Risks & open items for Rahul

1. **Font inlining now or later?** Shipping v0 with Georgia/SF Mono fallbacks is functional but visually weaker than the prototype. Inlining Spectral as base64 WOFF2 adds ~480 kb across four weights but is a one-time cost. Recommend deferring to v0.5 unless Rahul wants the visual fidelity from the first build.
2. **Branch summary field.** `branch-template.md` does not currently include a `summary:` frontmatter key, but the decision card needs one. Either: (a) add `summary:` to the template (preferred — explicit), or (b) auto-generate from `title` (lossy). Surface to `branch-drafter` agent and update template if (a).
3. **Multiple branches at the same fork paragraph.** The ledger allows it; the prototype CSS does not handle it. Flagged for `html-css-architect` once a real beat has co-located forks.
4. **Beat-numbered section IDs.** The prototype uses `s1`/`s2`/`s3` (Beat-5-only namespace). The build uses `b1-s1`, `b2-s1`, … to scope per beat. Animation engine references will need the small adapter in §3.9.
5. **Mistune block-level vs. inline.** Mistune treats `*foo*` as inline `<em>` and `*\nfoo\n*` (whole-paragraph italic) as a paragraph of `<em>`. The build's coda-detection logic must check "paragraph whose only child is an `<em>` whose text spans the whole content" — straightforward but worth a unit test.

---

## 6. Build file scaffold (for reference; not yet written)

```
build/
├── build.py                    # entrypoint
├── requirements.txt            # mistune>=3.0,<4.0  PyYAML>=6.0
├── parse_canon.py              # canon md → structured tree
├── parse_branch.py             # branch md → frontmatter + prose
├── verify_fork.py              # fork-at exact-match check
├── splice.py                   # canon + branches → spliced HTML
├── render.py                   # spliced tree → final HTML w/ inlined CSS+JS
└── tests/
    ├── test_fork_match.py
    ├── test_splice.py
    └── test_idempotent.py
```

Ship `build.py` as a single file for v0 and split into the modules above only if it grows past ~600 lines.

---

## 7. What's *not* in v0

- No watch mode / hot reload.
- No partial-build cache.
- No font inlining (system fallbacks only — see risk 1).
- No multi-branch-per-fork CSS (one fork → one branch).
- No build of the per-chapter standalone files mentioned in some earlier discussions — the Forest Edition is the only output.
- No PDF / EPUB. HTML only.

These are explicitly deferred. If Rahul wants any of them in v0, surface before writing code.

---

## 8. Sign-off criteria for build.py v0

- [ ] Three placeholder branches integrated end-to-end.
- [ ] Output is a single HTML file with no external dependencies (Google Fonts removed; system fonts used).
- [ ] Fork-at mismatch produces a precise error and exit code 1.
- [ ] Build is byte-identical on rerun (idempotent).
- [ ] Animation runs (split-flap on branch select), state persists, return-to-canon works — all verified by `prototype-tester`.
- [ ] All checks in `process/quality-gates.md` §3 pass.
