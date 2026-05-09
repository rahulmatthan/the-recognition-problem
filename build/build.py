#!/usr/bin/env python3
"""
build.py — Recognition Forest build pipeline (v0)

Produces build/recognition-problem.html from:
  - canon/*.md
  - branches/**/*.md (status: Locked only)
  - prototype/index-v4.html (template/shell, with system fonts substituted)

Spec: process/audit-build.md
Decisions: process/decisions.md (A: system fonts; B: summary; C: placeholders; D: switching)

Usage: python3 build/build.py
"""

import difflib
import hashlib
import html as html_lib
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import mistune
import yaml

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
CANON_DIR = ROOT / "canon"
BRANCHES_DIR = ROOT / "branches"
BUILD_DIR = ROOT / "build"
OUT_FILE = BUILD_DIR / "recognition-problem.html"


# -----------------------------------------------------------------------------
# Data classes
# -----------------------------------------------------------------------------

@dataclass
class Paragraph:
    """A canon paragraph after parsing. id is stable: bN-sK-pJ."""
    id: str
    text: str           # plain text (for fork match)
    html: str           # rendered HTML (inline only — no <p> wrapper)
    is_coda: bool = False


@dataclass
class Section:
    id: str             # bN-sK
    paragraphs: list = field(default_factory=list)


@dataclass
class Beat:
    n: int                                          # 1..10
    title: str = ""                                 # H1
    subtitle: str = ""                              # H3
    dateline: str = ""                              # *2027*
    sections: list = field(default_factory=list)    # Section[]


@dataclass
class Branch:
    id: str
    beat: int
    title: str
    summary: str
    fork_at: str            # raw frontmatter
    type: str
    length_target: str
    status: str
    prose_paragraphs: list  # list of (html, is_coda)
    file_path: Path
    # Resolved at integration time:
    fork_paragraph_id: str = ""     # bN-sK-pJ
    fork_section_id: str = ""       # bN-sK


# -----------------------------------------------------------------------------
# Frontmatter
# -----------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def split_frontmatter(text: str):
    """Returns (frontmatter_dict_or_None, body_str)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML frontmatter: {e}")
    return fm, m.group(2)


# -----------------------------------------------------------------------------
# Whitespace normalization for fork comparison
# -----------------------------------------------------------------------------

def normalize_ws(s: str) -> str:
    """Trim + collapse internal whitespace runs to single space. No other changes."""
    return re.sub(r"\s+", " ", s.strip())


# -----------------------------------------------------------------------------
# Markdown rendering helpers
# -----------------------------------------------------------------------------

# Build a mistune renderer once. We use the default HTMLRenderer; it emits
# <em> for *italic*, <p> for paragraphs, <hr/> for ---. We post-process.
_md = mistune.create_markdown(renderer="html", plugins=[])

# Strip <p>...</p> wrapper from a single-paragraph HTML chunk.
_PARA_WRAP_RE = re.compile(r"^\s*<p>(.*)</p>\s*$", re.DOTALL)
# Detect a paragraph whose entire content is a single <em>...</em> (italic coda).
_EM_ONLY_RE = re.compile(r"^\s*<em>(.*)</em>\s*$", re.DOTALL)


def _strip_para_wrap(s: str) -> str:
    m = _PARA_WRAP_RE.match(s)
    return m.group(1) if m else s


def _is_em_only(inner_html: str) -> bool:
    """True if the inline HTML is wholly a single <em>...</em> with no other
    siblings — used to identify italic-coda paragraphs."""
    inner = inner_html.strip()
    m = _EM_ONLY_RE.match(inner)
    if not m:
        return False
    # Reject if there are additional <em> tags or other tags outside the match.
    # The regex is greedy; we additionally require no </em> earlier than the close.
    # Simple heuristic: the only tag occurrences should be the opening <em> and closing </em>.
    if inner.count("<em>") == 1 and inner.count("</em>") == 1:
        return True
    return False


def _html_to_plain(html: str) -> str:
    """Strip tags and decode entities for fork-text comparison."""
    no_tags = re.sub(r"<[^>]+>", "", html)
    return html_lib.unescape(no_tags)


# -----------------------------------------------------------------------------
# Canon parsing
# -----------------------------------------------------------------------------

BEAT_FILE_RE = re.compile(r"^beat(\d+)-draft-v\d+\.md$")


def parse_canon_file(path: Path) -> Beat:
    m = BEAT_FILE_RE.match(path.name)
    if not m:
        raise ValueError(f"Canon filename does not match beatN-draft-vM.md: {path.name}")
    beat_n = int(m.group(1))

    raw = path.read_text(encoding="utf-8")
    _, body = split_frontmatter(raw)  # canon may or may not have frontmatter

    # Render markdown to HTML
    rendered = _md(body)

    # Parse the rendered HTML by walking top-level blocks. We do a simple
    # block-level split using a tag-aware regex over <hN>, <p>, <hr/>.
    # mistune's output is flat at the top level for our subset of markdown.
    blocks = _split_top_level_blocks(rendered)

    beat = Beat(n=beat_n)

    # Extract H1, H3, dateline (italic-only paragraph) from the leading blocks.
    section_idx = 0
    current_section: Section | None = None
    paragraph_idx = 0
    seen_dateline = False

    for tag, content in blocks:
        if tag == "h1" and not beat.title:
            beat.title = _html_to_plain(content).strip()
            continue
        if tag == "h3" and not beat.subtitle:
            beat.subtitle = _html_to_plain(content).strip()
            continue
        if tag == "p" and not seen_dateline and _is_em_only(content):
            # First italic-only paragraph in the file is the dateline.
            beat.dateline = _html_to_plain(content).strip()
            seen_dateline = True
            continue
        if tag == "hr":
            # Section break: open a new section
            if current_section is not None:
                beat.sections.append(current_section)
            section_idx += 1
            current_section = Section(id=f"b{beat_n}-s{section_idx}")
            paragraph_idx = 0
            continue
        if tag == "p":
            # Paragraph in the current section. If we haven't opened a section
            # yet (canon prose before the first ---), open section 1 implicitly.
            if current_section is None:
                section_idx = 1
                current_section = Section(id=f"b{beat_n}-s{section_idx}")
                paragraph_idx = 0
            paragraph_idx += 1
            inner = content
            is_coda = _is_em_only(inner)
            text = _html_to_plain(inner)
            para = Paragraph(
                id=f"{current_section.id}-p{paragraph_idx}",
                text=text,
                html=inner,
                is_coda=is_coda,
            )
            current_section.paragraphs.append(para)
            continue
        # Other tags (h2, lists, blockquotes) — ignore for now; canon doesn't use them.

    if current_section is not None:
        beat.sections.append(current_section)

    return beat


# Top-level block splitter: extracts <h1>, <h3>, <p>, <hr/> from rendered HTML.
# mistune output places these flush at the top level, separated by newlines.
_BLOCK_RE = re.compile(
    r"<(h[1-6])>(.*?)</\1>"
    r"|<p>(.*?)</p>"
    r"|<hr\s*/?>",
    re.DOTALL,
)


def _split_top_level_blocks(rendered: str):
    """Yield (tag, inner_html) tuples for h1..h6, p, hr in document order."""
    out = []
    for m in _BLOCK_RE.finditer(rendered):
        if m.group(1):  # heading
            out.append((m.group(1), m.group(2)))
        elif m.group(3) is not None:  # paragraph
            out.append(("p", m.group(3)))
        else:
            out.append(("hr", ""))
    return out


# -----------------------------------------------------------------------------
# Branch parsing
# -----------------------------------------------------------------------------

REQUIRED_BRANCH_FIELDS = ["id", "beat", "title", "summary", "fork_at", "type", "length_target", "status"]


def parse_branch_file(path: Path) -> Branch | None:
    raw = path.read_text(encoding="utf-8")
    fm, body = split_frontmatter(raw)
    if fm is None:
        raise ValueError(f"{path}: missing frontmatter")

    missing = [k for k in REQUIRED_BRANCH_FIELDS if k not in fm]
    if missing:
        raise ValueError(f"{path}: frontmatter missing required fields: {missing}")

    status = str(fm["status"]).strip()
    if status.lower() != "locked":
        print(f"  skipping {path.relative_to(ROOT)} (status: {status})", file=sys.stderr)
        return None

    # Extract just the "## Branch prose" section from the body.
    # Skip everything before "## Branch prose" and everything from "## Drafting notes" onward.
    prose_section = _extract_section(body, "Branch prose", stop_at=("Drafting notes", "Self-review", "Review log"))
    if not prose_section:
        raise ValueError(f"{path}: '## Branch prose' section is empty or missing")

    # Render prose markdown
    rendered = _md(prose_section)
    blocks = _split_top_level_blocks(rendered)

    prose_paragraphs = []
    saw_hr = False
    for tag, content in blocks:
        if tag == "hr":
            saw_hr = True
            continue
        if tag == "p":
            inner = content
            is_coda = _is_em_only(inner) and saw_hr
            prose_paragraphs.append((inner, is_coda))
        # Headings inside Branch prose: ignore (the # Branch: title heading was filtered above)

    branch = Branch(
        id=str(fm["id"]),
        beat=int(fm["beat"]),
        title=str(fm["title"]),
        summary=str(fm["summary"]),
        fork_at=str(fm["fork_at"]),
        type=str(fm["type"]),
        length_target=str(fm["length_target"]),
        status=status,
        prose_paragraphs=prose_paragraphs,
        file_path=path,
    )
    return branch


def _extract_section(body: str, heading_text: str, stop_at=()):
    """Return the body of the markdown section beginning with `## <heading_text>`,
    stopping at the next H2 in stop_at (or any H2 if stop_at is empty)."""
    lines = body.splitlines()
    start = None
    heading_re = re.compile(rf"^##\s+{re.escape(heading_text)}\s*$")
    for i, line in enumerate(lines):
        if heading_re.match(line):
            start = i + 1
            break
    if start is None:
        return ""
    out = []
    h2_re = re.compile(r"^##\s+(.+?)\s*$")
    h1_re = re.compile(r"^#\s+")
    for line in lines[start:]:
        m = h2_re.match(line)
        if m:
            stop_name = m.group(1).strip()
            if not stop_at or stop_name in stop_at:
                break
            # Otherwise: another H2 we don't recognise — also stop, conservatively.
            break
        if h1_re.match(line):
            # An H1 inside the body shouldn't happen, but be safe.
            break
        out.append(line)
    return "\n".join(out)


# -----------------------------------------------------------------------------
# Fork-paragraph verification
# -----------------------------------------------------------------------------

def verify_fork_paragraph(branch: Branch, beats_by_n: dict) -> None:
    """Match branch.fork_at against canon paragraphs of the branch's beat.
    Raises a build-failing exception with a difflib-driven error on mismatch.
    Sets branch.fork_paragraph_id and branch.fork_section_id on success."""
    if branch.beat not in beats_by_n:
        raise BuildError(
            f"Branch {branch.file_path.relative_to(ROOT)}: "
            f"references beat {branch.beat} but canon for that beat was not parsed."
        )
    beat = beats_by_n[branch.beat]
    target = normalize_ws(branch.fork_at)

    matches = []
    flat = []
    for section in beat.sections:
        for para in section.paragraphs:
            flat.append((section, para))
            if normalize_ws(para.text) == target:
                matches.append((section, para))

    if len(matches) == 1:
        section, para = matches[0]
        branch.fork_paragraph_id = para.id
        branch.fork_section_id = section.id
        return

    # Build a precise error.
    rel_branch = branch.file_path.relative_to(ROOT)
    canon_path_rel = f"canon/beat{branch.beat}-draft-vN.md"

    if len(matches) > 1:
        ids = ", ".join(p.id for _, p in matches)
        raise BuildError(
            f"\nERROR: branch {rel_branch} fork_at matches MULTIPLE canon paragraphs: {ids}\n"
            f"  fork_at must uniquely identify a paragraph. Add or alter context.\n"
        )

    # No match. Find the closest paragraph by normalized text.
    candidates = [normalize_ws(p.text) for _, p in flat]
    close = difflib.get_close_matches(target, candidates, n=1, cutoff=0.0)
    closest_text = close[0] if close else "(no canon paragraphs found)"
    closest_para = None
    if close:
        for s, p in flat:
            if normalize_ws(p.text) == close[0]:
                closest_para = p
                break

    # First differing character
    first_diff = _first_diff_index(target, closest_text)
    if first_diff is not None and first_diff < len(target) and first_diff < len(closest_text):
        exp_ch = target[first_diff]
        got_ch = closest_text[first_diff]
        diff_line = (
            f"  First differing character: position {first_diff}.\n"
            f"  expected ch:  {exp_ch!r} (U+{ord(exp_ch):04X})\n"
            f"  canon    ch:  {got_ch!r} (U+{ord(got_ch):04X})\n"
        )
    else:
        diff_line = (
            f"  Lengths differ. expected {len(target)} chars, canon {len(closest_text)} chars.\n"
        )

    closest_id = closest_para.id if closest_para else "(unknown)"
    raise BuildError(
        f"\nERROR: {rel_branch} fork_at does not match canon.\n\n"
        f"  branch:  {rel_branch}\n"
        f"  canon:   {canon_path_rel}  (beat {branch.beat})\n\n"
        f"  Expected (from branch frontmatter, normalized):\n"
        f"    {_truncate(target, 240)}\n\n"
        f"  Closest canon paragraph (id {closest_id}):\n"
        f"    {_truncate(closest_text, 240)}\n\n"
        f"{diff_line}\n"
        f"  Fix: copy the canon paragraph verbatim into the branch's fork_at field.\n"
        f"  The build refuses to splice on mismatch.\n"
    )


def _first_diff_index(a: str, b: str):
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return i
    if len(a) != len(b):
        return n
    return None


def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[:n] + "..."


class BuildError(Exception):
    pass


# -----------------------------------------------------------------------------
# Splice + HTML emit
# -----------------------------------------------------------------------------

ROMAN = ["", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x",
         "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx"]


def render_paragraph_html(para: Paragraph, fork_branches=None) -> str:
    """Render a canon paragraph to HTML. If fork_branches is provided, attach
    a branch-mark button for each branch (decision card is emitted separately)."""
    cls = []
    attrs = []
    if para.is_coda:
        cls.append("branch-coda-line")
    if fork_branches:
        cls.append("fork-paragraph")
        # Single-branch case is the common one (per audit). For multiple, append all.
        attrs.append(f'data-fork="{fork_branches[0].id}"')
    cls_attr = f' class="{" ".join(cls)}"' if cls else ""
    attr_str = (" " + " ".join(attrs)) if attrs else ""
    inner = para.html
    # Append branch-mark buttons inside the paragraph
    button_html = ""
    if fork_branches:
        for b in fork_branches:
            button_html += (
                f'<button class="branch-mark" data-branch="{b.id}" '
                f'aria-label="A branch is available here">'
                f'<span class="label">branch</span></button>'
            )
    return f'<p id="{para.id}"{cls_attr}{attr_str}>{inner}{button_html}</p>'


def render_decision_card(branch: Branch) -> str:
    summary_html = html_lib.escape(branch.summary)
    name_html = html_lib.escape(branch.title)
    return (
        f'<div class="decision" id="decision-{branch.id}">'
        f'<div class="decision-inner">'
        f'<div class="decision-title">Branch · {name_html}</div>'
        f'<div class="decision-summary">{summary_html}</div>'
        f'<div class="decision-actions">'
        f'<button class="decision-btn primary" data-action="commit" data-branch="{branch.id}">Follow this branch</button>'
        f'<button class="decision-btn" data-action="cancel" data-branch="{branch.id}">Stay with canon</button>'
        f'</div></div></div>'
    )


def render_section_html(section: Section, branches_in_section: list, beat_n: int, section_idx: int) -> str:
    """Render one section: section-mark, pre-fork paragraphs, fork paragraph(s)
    with marginal mark + decision card + post-fork div, then post-fork paragraphs.

    branches_in_section: list of Branch objects whose fork is in this section."""
    # Group branches by fork_paragraph_id
    branches_by_fork_para = {}
    for b in branches_in_section:
        branches_by_fork_para.setdefault(b.fork_paragraph_id, []).append(b)

    # Determine the earliest fork paragraph in this section (defines where post-fork begins).
    fork_para_ids_in_order = []
    for para in section.paragraphs:
        if para.id in branches_by_fork_para:
            fork_para_ids_in_order.append(para.id)

    out = []
    out.append(f'<section class="section" id="{section.id}">')
    out.append(f'<div class="section-mark">{ROMAN[section_idx]}</div>')

    # If there are no forks in this section, render all paragraphs straight.
    if not fork_para_ids_in_order:
        for para in section.paragraphs:
            out.append(render_paragraph_html(para))
        out.append('</section>')
        return "\n".join(out)

    # If forks exist, we render up to and including the earliest fork paragraph,
    # insert decision card(s) and post-fork div, then move remaining paragraphs
    # of this section into the post-fork div.
    earliest_fork_id = fork_para_ids_in_order[0]
    branches_at_fork = branches_by_fork_para[earliest_fork_id]

    # Find index of earliest fork paragraph
    fork_idx = next(i for i, p in enumerate(section.paragraphs) if p.id == earliest_fork_id)

    # Pre-fork paragraphs (before the fork)
    for para in section.paragraphs[:fork_idx]:
        out.append(render_paragraph_html(para))

    # Fork paragraph itself, with mark(s)
    fork_para = section.paragraphs[fork_idx]
    out.append(render_paragraph_html(fork_para, fork_branches=branches_at_fork))

    # Decision card(s) for each branch at this fork
    for b in branches_at_fork:
        out.append(render_decision_card(b))

    # Post-fork div (one per branch — matches prototype's data-fork-target convention).
    # When canon is on screen, all post-fork divs hold identical canon content.
    post_fork_paras = section.paragraphs[fork_idx + 1:]
    post_fork_inner = "\n".join(render_paragraph_html(p) for p in post_fork_paras)
    for b in branches_at_fork:
        out.append(
            f'<div class="post-fork" data-fork-target="{b.id}" data-section="{section.id}">\n'
            f'{post_fork_inner}\n</div>'
        )

    out.append('</section>')
    return "\n".join(out)


def render_beat_html(beat: Beat, branches_for_beat: list) -> str:
    """Render one beat as a <article> wrapper inner block. branches_for_beat is
    a list of Branch with fork resolved."""
    out = []
    # Beat-level header
    out.append(f'<div class="beat" id="b{beat.n}">')
    out.append(f'<header class="beat-header">')
    if beat.title:
        out.append(f'<h1 class="beat-title">{html_lib.escape(beat.title)}</h1>')
    if beat.subtitle:
        out.append(f'<div class="beat-subtitle">{html_lib.escape(beat.subtitle)}</div>')
    if beat.dateline:
        out.append(f'<div class="beat-dateline"><em>{html_lib.escape(beat.dateline)}</em></div>')
    out.append('</header>')

    # Group branches by section
    by_section = {}
    for b in branches_for_beat:
        by_section.setdefault(b.fork_section_id, []).append(b)

    for idx, section in enumerate(beat.sections, start=1):
        branches_in_section = by_section.get(section.id, [])
        out.append(render_section_html(section, branches_in_section, beat.n, idx))

    out.append('</div>')  # /beat
    return "\n".join(out)


# -----------------------------------------------------------------------------
# JS BRANCHES object emit
# -----------------------------------------------------------------------------

def js_str(s: str) -> str:
    """Escape string for JS source as a JSON-style double-quoted string."""
    out = []
    for ch in s:
        if ch == "\\":
            out.append("\\\\")
        elif ch == '"':
            out.append('\\"')
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif ch == " ":
            out.append("\\u2028")
        elif ch == " ":
            out.append("\\u2029")
        elif ord(ch) < 0x20:
            out.append(f"\\u{ord(ch):04x}")
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def render_branches_object(branches: list, beats_by_n: dict) -> str:
    """Emit the BRANCHES JS object literal in the new shape:
       { id, name, summary, fork: {sectionId, afterParagraph}, affects: { sectionId: { fromParagraph, paragraphs[] } } }
    `paragraphs` is an array of inner-HTML strings (one per <p>)."""
    lines = ["const BRANCHES = {"]
    # Sort by id for determinism
    for branch in sorted(branches, key=lambda b: b.id):
        beat = beats_by_n[branch.beat]
        # Locate fork section + para
        fork_section = next(s for s in beat.sections if s.id == branch.fork_section_id)
        fork_para_idx = next(i for i, p in enumerate(fork_section.paragraphs) if p.id == branch.fork_paragraph_id)

        # Build the affects map.
        # - Fork section: post-fork paragraphs come from branch prose UP TO the next section,
        #   replacing canon paragraphs after the fork.
        # - Subsequent sections: branch prose continues. For v0, simple model — the branch's
        #   prose paragraphs are split: paragraphs before any branch-internal section break
        #   replace the fork section; remaining paragraphs replace subsequent sections in order.
        # Currently branch markdown does NOT carry section-break --- in its prose; the v0
        # convention is: ALL branch prose paragraphs (including coda) replace the fork section's
        # post-fork paragraphs. Downstream sections fall back to canon.
        #
        # If a branch wishes to affect downstream sections, it must carry a horizontal rule
        # (---) in the prose AFTER the chapter-prose-replacement and BEFORE the coda. The
        # parser already marks post-rule paragraphs as is_coda=True. For v0 these are placed
        # in a synthetic "next section" entry only if there's a next canon section.
        #
        # v0 simplification: we put ALL branch prose paragraphs (incl. coda) into a single
        # affects entry for the fork section. The downstream model is reserved for v0.5
        # once a real branch needs it.

        affects_lines = []

        # Decide which paragraphs go to which sections.
        # Heuristic: split branch prose into [main, coda]. Main → fork section. Coda → either
        # fork section (default) or next section (if next section exists).
        main_paras = [(h, c) for (h, c) in branch.prose_paragraphs if not c]
        coda_paras = [(h, c) for (h, c) in branch.prose_paragraphs if c]

        # Fork section paragraphs (HTML strings): main_paras as <p>...</p>; coda goes here too
        # for v0 (to keep the splice mechanism dead-simple). Coda gets the special class.
        fork_section_html = []
        for (h, _) in main_paras:
            fork_section_html.append(f"<p>{h}</p>")
        for (h, _) in coda_paras:
            fork_section_html.append(f'<p class="branch-coda-line">{h}</p>')

        # First post-fork canon paragraph id (for fromParagraph)
        if fork_para_idx + 1 < len(fork_section.paragraphs):
            from_para = fork_section.paragraphs[fork_para_idx + 1].id
        else:
            from_para = ""  # fork is at end of section

        affects_lines.append(f'    {js_str(branch.fork_section_id)}: {{')
        affects_lines.append(f'      fromParagraph: {js_str(from_para)},')
        affects_lines.append(f'      paragraphs: [')
        for h in fork_section_html:
            affects_lines.append(f'        {js_str(h)},')
        affects_lines.append(f'      ]')
        affects_lines.append(f'    }}')

        affects_block = "\n".join(affects_lines)

        lines.append(f'  {js_str(branch.id)}: {{')
        lines.append(f'    id: {js_str(branch.id)},')
        lines.append(f'    name: {js_str(branch.title)},')
        lines.append(f'    summary: {js_str(branch.summary)},')
        lines.append(f'    fork: {{ sectionId: {js_str(branch.fork_section_id)}, afterParagraph: {js_str(branch.fork_paragraph_id)} }},')
        lines.append(f'    affects: {{')
        lines.append(affects_block)
        lines.append(f'    }}')
        lines.append(f'  }},')
    lines.append("};")
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# HTML page emit (self-contained)
# -----------------------------------------------------------------------------

# CSS lifted from prototype/index-v4.html, with Google Fonts replaced by system stacks.
# System serif: Iowan Old Style / Charter / Georgia → serif fallback (Decision A).
# System mono: SF Mono / Monaco / Menlo → monospace fallback.
CSS = r"""
:root {
  --paper: #f4f0e6;
  --paper-deep: #ebe5d4;
  --ink: #1a1612;
  --ink-soft: #4a4036;
  --ink-faint: #8a7d6a;
  --branch: #8b3a2e;
  --branch-faint: #b8a896;
  --branch-spent: #c4b8a3;
  --rule: #d4c9b0;
  --max-text: 38rem;
  --serif: 'Iowan Old Style', 'Charter', Georgia, 'Times New Roman', serif;
  --mono: ui-monospace, 'SF Mono', Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 17px; scroll-behavior: smooth; }

body {
  font-family: var(--serif);
  font-weight: 400;
  background: var(--paper);
  color: var(--ink);
  line-height: 1.65;
  min-height: 100vh;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-image:
    radial-gradient(at 20% 10%, rgba(139, 58, 46, 0.02) 0%, transparent 50%),
    radial-gradient(at 80% 90%, rgba(26, 22, 18, 0.025) 0%, transparent 50%);
}

body::before {
  content: "";
  position: fixed; inset: 0;
  pointer-events: none; opacity: 0.35; z-index: 1;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/><feColorMatrix values='0 0 0 0 0.1, 0 0 0 0 0.08, 0 0 0 0 0.06, 0 0 0 0.04 0'/></filter><rect width='100%25' height='100%25' filter='url(%23n)'/></svg>");
  mix-blend-mode: multiply;
}

.container { max-width: 64rem; margin: 0 auto; padding: 4rem 2rem 8rem; position: relative; z-index: 2; }

/* Masthead */
.masthead { text-align: center; margin-bottom: 5rem; padding-bottom: 2.5rem; border-bottom: 1px solid var(--rule); position: relative; }
.imprint {
  font-family: var(--mono);
  font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.18em;
  color: var(--ink-faint); margin-bottom: 1.8rem; transition: color 0.4s;
}
.masthead h1 {
  font-family: var(--serif);
  font-weight: 300; font-style: italic;
  font-size: clamp(1.8rem, 4vw, 2.8rem); letter-spacing: -0.01em;
  margin-bottom: 0.6rem; color: var(--ink); transition: color 0.4s;
}
.beat-number {
  font-family: var(--mono);
  font-size: 0.75rem; letter-spacing: 0.25em; text-transform: uppercase;
  color: var(--ink-soft); transition: color 0.4s;
}

body.branched .imprint { color: var(--branch); }
body.branched .beat-number { color: var(--branch); }

.return-to-canon {
  display: none; margin-top: 1.2rem;
  background: none; border: 1px solid var(--branch); color: var(--branch);
  font-family: var(--mono);
  font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase;
  padding: 0.55rem 1.1rem; cursor: pointer; transition: all 0.25s; border-radius: 1px;
}
body.branched .return-to-canon { display: inline-block; }
.return-to-canon:hover { background: var(--branch); color: var(--paper); }
.return-to-canon:disabled { opacity: 0.5; cursor: wait; }

.note {
  max-width: var(--max-text); margin: 0 auto 4rem;
  font-style: italic; font-size: 0.92rem; color: var(--ink-soft);
  line-height: 1.7; text-align: center; padding: 0 1rem;
}
.note .key-mark {
  display: inline-block; width: 2px; height: 0.95em;
  background: var(--branch); vertical-align: -0.05em; margin: 0 0.15em;
}

article { max-width: var(--max-text); margin: 0 auto; position: relative; }

/* Beat header (per-chapter) */
.beat { margin-bottom: 7rem; }
.beat-header { text-align: center; margin: 4rem 0 3rem; }
.beat-title { font-family: var(--serif); font-weight: 300; font-style: italic; font-size: clamp(1.6rem, 3.5vw, 2.4rem); margin-bottom: 0.4rem; color: var(--ink); }
.beat-subtitle { font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.22em; text-transform: uppercase; color: var(--ink-soft); margin-bottom: 0.5rem; }
.beat-dateline { font-style: italic; font-size: 0.85rem; color: var(--ink-faint); }

.section { margin-bottom: 5rem; position: relative; }

.section-mark {
  font-family: var(--mono);
  font-size: 0.7rem; letter-spacing: 0.2em; color: var(--ink-faint);
  text-transform: uppercase; margin-bottom: 1.5rem; text-align: center;
}
.section-mark::before, .section-mark::after { content: "\2014"; margin: 0 0.8rem; color: var(--branch-faint); }

p {
  margin-bottom: 1.4rem; font-size: 1.05rem; line-height: 1.75;
  text-wrap: pretty; hyphens: auto; position: relative;
}

em { font-style: italic; }

.fork-paragraph { position: relative; }

.branch-mark {
  position: absolute; right: -2.8rem; top: 0.45rem;
  width: 1.8rem; height: 100%;
  cursor: pointer; display: flex; align-items: flex-start;
  padding-top: 0.3em; z-index: 5;
  background: transparent; border: none;
  font-family: var(--mono);
}

.branch-mark::before {
  content: ""; display: block;
  width: 1px; height: 2.8em;
  background: var(--branch);
  transition: width 0.3s ease, height 0.3s ease;
}

.branch-mark:hover::before, .branch-mark:focus::before { width: 2px; height: 3.4em; }

.branch-mark .label {
  position: absolute; left: 1.2rem; top: 0.4em;
  font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--branch); white-space: nowrap;
  opacity: 0; transition: opacity 0.3s ease; pointer-events: none;
}
.branch-mark:hover .label, .branch-mark:focus .label { opacity: 1; }

body.branched .branch-mark, body.animating .branch-mark {
  pointer-events: none; opacity: 0.25;
}
body.branched .branch-mark.active-branch { opacity: 0; display: none; }

/* Decision card */
.decision {
  max-height: 0; overflow: hidden;
  transition: max-height 0.45s cubic-bezier(0.4, 0, 0.2, 1), margin 0.45s ease;
  margin: 0;
}
.decision.open { max-height: 400px; margin: 1.4rem 0 1.6rem; }
.decision-inner {
  background: var(--paper-deep); border-left: 2px solid var(--branch);
  padding: 1.4rem 1.6rem;
  opacity: 0; transform: translateY(-6px);
  transition: opacity 0.4s ease 0.15s, transform 0.4s ease 0.15s;
}
.decision.open .decision-inner { opacity: 1; transform: translateY(0); }
.decision-title {
  font-family: var(--mono);
  font-size: 0.65rem; letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--branch); margin-bottom: 0.7rem;
}
.decision-summary { font-style: italic; color: var(--ink-soft); font-size: 0.95rem; line-height: 1.6; margin-bottom: 1.2rem; }
.decision-actions { display: flex; gap: 0.8rem; flex-wrap: wrap; }
.decision-btn {
  background: none; border: 1px solid var(--ink-soft); color: var(--ink-soft);
  font-family: var(--mono);
  font-size: 0.65rem; letter-spacing: 0.18em; text-transform: uppercase;
  padding: 0.6rem 1rem; cursor: pointer; transition: all 0.2s; border-radius: 1px;
}
.decision-btn:hover { background: var(--ink); color: var(--paper); border-color: var(--ink); }
.decision-btn.primary { border-color: var(--branch); color: var(--branch); }
.decision-btn.primary:hover { background: var(--branch); color: var(--paper); border-color: var(--branch); }

/* SPLIT-FLAP / AIRPORT-BOARD ANIMATION STATE */

p.flapping {
  font-family: var(--mono);
  font-weight: 400;
  font-size: 0.93rem;
  line-height: 1.85;
  letter-spacing: 0.005em;
  color: var(--ink-soft);
  text-wrap: auto;
  hyphens: none;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.flap-ch {
  display: inline-block;
  min-width: 0.58ch;
  text-align: center;
  color: var(--branch);
  transition: color 0.18s ease;
  font-variant-numeric: tabular-nums;
}

.flap-ch.settled {
  color: var(--ink);
}

.flap-ch:not(.settled) {
  text-shadow: 0 0 0.5px rgba(139, 58, 46, 0.25);
}

/* Coda line styling preserved */
.branch-coda-line {
  font-family: var(--mono);
  font-size: 0.78rem; color: var(--ink-faint);
  line-height: 1.65; font-style: normal;
  display: block;
  margin-top: 1.6rem; padding-top: 1.4rem;
  border-top: 1px solid var(--rule);
}
.branch-coda-line::before { content: "\2192 "; color: var(--branch); margin-right: 0.3em; }
.branch-coda-line em { font-style: italic; color: var(--ink-soft); }

/* status pulse during animation */
.rewriting-pulse {
  position: fixed; bottom: 2rem; left: 50%; transform: translateX(-50%);
  font-family: var(--mono);
  font-size: 0.65rem; letter-spacing: 0.22em; text-transform: uppercase;
  color: var(--branch);
  opacity: 0; transition: opacity 0.4s; z-index: 100;
  background: var(--paper); padding: 0.5rem 1rem;
  border: 1px solid var(--branch); border-radius: 1px;
}
.rewriting-pulse.show { opacity: 1; }
.rewriting-pulse .dot {
  display: inline-block; width: 4px; height: 4px;
  background: var(--branch); border-radius: 50%; margin-left: 0.4rem;
  animation: pulse 1.2s infinite;
}
@keyframes pulse { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }

footer {
  max-width: var(--max-text); margin: 6rem auto 0;
  padding-top: 3rem; border-top: 1px solid var(--rule);
  text-align: center;
  font-family: var(--mono);
  font-size: 0.7rem; letter-spacing: 0.18em; text-transform: uppercase;
  color: var(--ink-faint);
}
.branch-status { margin-bottom: 1rem; }
.branch-status .branch-name { color: var(--branch); }
.system-note {
  font-style: italic; text-transform: none; letter-spacing: normal;
  font-family: var(--serif); font-size: 0.85rem; color: var(--ink-faint);
  margin-top: 1.5rem; line-height: 1.6; min-height: 2em;
  transition: opacity 0.6s ease; opacity: 0;
}
.system-note.visible { opacity: 1; }

@media (max-width: 720px) {
  .container { padding: 2rem 1.5rem 5rem; }
  .masthead { margin-bottom: 3rem; }
  .note { margin-bottom: 2.5rem; }
  .section { margin-bottom: 3.5rem; }
  .branch-mark { right: auto; left: -1.6rem; width: 1.2rem; }
  .branch-mark .label { left: -2rem; top: 3.2em; }
  .flap-ch { min-width: 0.55ch; }
}

.branch-mark:focus-visible { outline: 2px solid var(--branch); outline-offset: 4px; border-radius: 1px; }
.branch-mark:focus { outline: none; }
"""


# Animation + branch orchestration JS. Adapted from prototype/index-v4.html.
# Key differences from prototype:
#   - BRANCHES schema is the new shape: { id, name, summary, fork: {sectionId, afterParagraph}, affects: { sectionId: { fromParagraph, paragraphs[] } } }
#   - getReplacementForSection() reads from affects[sectionId].paragraphs
#   - Switching dynamic (Decision D): no A→B chain. To pick a different branch,
#     reader must reset first. Branch marks are hidden when in a branch.
JS_TEMPLATE = r"""
//================================================================
// BRANCH CONTENT (build-generated)
//================================================================
__BRANCHES_OBJECT__

const STORAGE_KEY = 'forest-state-v0';

let state = { branch: null };

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) state = JSON.parse(raw);
  } catch (e) {}
}
function saveState() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); }
  catch (e) {}
}

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

//================================================================
// SPLIT-FLAP / AIRPORT-BOARD ANIMATION
//================================================================

const FLAP_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.,;:—';
const TICK_MS = 50;
const MIN_FLIPS = 5;
const MAX_FLIPS = 22;
const PARAGRAPH_OVERLAP = 0.55;

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function randomFlapChar() { return FLAP_CHARS[Math.floor(Math.random() * FLAP_CHARS.length)]; }
function htmlToPlainText(html) { const t = document.createElement('div'); t.innerHTML = html; return t.textContent || ''; }

function flapParagraph(pElement, targetHTML, onNearDone) {
  return new Promise(resolve => {
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
      span.textContent = initChar === ' ' ? ' ' : initChar;
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
          spans[i].textContent = t === ' ' ? ' ' : t;
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

function normalizeHTML(html) { const t = document.createElement('div'); t.innerHTML = html; return t.innerHTML.trim().replace(/\s+/g, ' '); }

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

//================================================================
// BRANCH ORCHESTRATION
//================================================================

// New schema adapter: returns array of paragraph-HTML strings to swap into the
// given section, or null if branch does not affect this section.
function getReplacementForSection(branchId, sectionId) {
  const branch = BRANCHES[branchId];
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
  const branch = BRANCHES[branchId];
  if (!branch) return [];
  const beatId = branch.fork.sectionId.split('-')[0]; // "b1" from "b1-s7"
  const allSections = Array.from(document.querySelectorAll(`section.section[id^="${beatId}-s"]`)).map(s => s.id);
  const idx = allSections.indexOf(branch.fork.sectionId);
  if (idx === -1) return [];
  return allSections.slice(idx);
}

async function commitBranch(branchId) {
  const branch = BRANCHES[branchId];
  if (!branch) return;
  document.body.classList.add('animating');
  const pulse = document.getElementById('pulse');
  pulse.firstChild.textContent = 'Rewriting';
  pulse.classList.add('show');

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
      if (fp) { fp.scrollIntoView({ behavior: 'smooth', block: 'center' }); await sleep(450); }
      await rewriteContainerParagraphs(postFork, replacement);
    } else {
      const section = document.getElementById(sId);
      if (!section) continue;
      const wrapper = ensureSectionContentWrapper(section);
      if (!hasAnyChange(wrapper, replacement)) continue;
      const firstChanged = findFirstChangedParagraph(wrapper, replacement);
      const target = firstChanged || section;
      target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      await sleep(500);
      await rewriteContainerParagraphs(wrapper, replacement);
    }
  }

  state.branch = branchId;
  saveState();
  applyBranchedUI();
  document.body.classList.remove('animating');
  pulse.classList.remove('show');
}

async function returnToCanon() {
  if (!state.branch) return;
  const branchId = state.branch;
  const branch = BRANCHES[branchId];
  if (!branch) { state.branch = null; saveState(); applyBranchedUI(); return; }

  document.body.classList.add('animating');
  const pulse = document.getElementById('pulse');
  pulse.firstChild.textContent = 'Restoring';
  pulse.classList.add('show');

  const sectionsToRewrite = listSectionsFromForkOnward(branchId);

  for (let i = 0; i < sectionsToRewrite.length; i++) {
    const sId = sectionsToRewrite[i];
    if (sId === branch.fork.sectionId) {
      const postFork = document.querySelector(`.post-fork[data-fork-target="${branchId}"]`);
      if (!postFork) continue;
      const tmp = document.createElement('div');
      tmp.innerHTML = canonSnapshot[branchId];
      const canonParas = Array.from(tmp.querySelectorAll(':scope > p')).map(p => p.outerHTML);
      if (!hasAnyChange(postFork, canonParas)) continue;
      const fp = document.querySelector(`.fork-paragraph[data-fork="${branchId}"]`);
      if (fp) { fp.scrollIntoView({ behavior: 'smooth', block: 'center' }); await sleep(450); }
      await rewriteContainerParagraphs(postFork, canonParas);
    } else {
      const section = document.getElementById(sId);
      if (!section) continue;
      const wrapper = ensureSectionContentWrapper(section);
      const fullCanon = canonSnapshot['__' + sId];
      const tmp = document.createElement('div'); tmp.innerHTML = fullCanon;
      const mark = tmp.querySelector('.section-mark'); if (mark) mark.remove();
      const canonParas = Array.from(tmp.querySelectorAll('p')).map(p => p.outerHTML);
      if (!hasAnyChange(wrapper, canonParas)) continue;
      const firstChanged = findFirstChangedParagraph(wrapper, canonParas);
      const target = firstChanged || section;
      target.scrollIntoView({ behavior: 'smooth', block: 'center' });
      await sleep(500);
      await rewriteContainerParagraphs(wrapper, canonParas);
    }
  }

  state.branch = null;
  saveState();
  applyBranchedUI();
  document.body.classList.remove('animating');
  pulse.classList.remove('show');
}

function applyBranchedUI() {
  const branchId = state.branch;
  const status = document.getElementById('status');
  const note = document.getElementById('systemNote');
  document.querySelectorAll('.branch-mark').forEach(m => m.classList.remove('active-branch'));
  if (branchId && BRANCHES[branchId]) {
    document.body.classList.add('branched');
    const name = BRANCHES[branchId].name;
    if (status) status.innerHTML = `Reading: <span class="branch-name">Branch · ${name}</span>`;
    const activeMark = document.querySelector(`.branch-mark[data-branch="${branchId}"]`);
    if (activeMark) activeMark.classList.add('active-branch');
    if (note) { note.textContent = "The system has noted your choice. The book has diverged."; note.classList.add('visible'); }
  } else {
    document.body.classList.remove('branched');
    if (status) status.innerHTML = `Reading: <span class="branch-name">canon</span>`;
    if (note) { note.classList.remove('visible'); note.textContent = ''; }
  }
}

//================================================================
// EVENTS
//================================================================

document.querySelectorAll('.branch-mark').forEach(mark => {
  mark.addEventListener('click', (e) => {
    e.stopPropagation();
    if (document.body.classList.contains('animating')) return;
    if (state.branch) return;  // Decision D: must reset to canon first
    const branchId = mark.getAttribute('data-branch');
    const decision = document.getElementById('decision-' + branchId);
    if (!decision) return;
    const isOpen = decision.classList.contains('open');
    document.querySelectorAll('.decision').forEach(d => d.classList.remove('open'));
    if (!isOpen) {
      decision.classList.add('open');
      setTimeout(() => decision.scrollIntoView({ behavior: 'smooth', block: 'center' }), 200);
    }
  });
});

document.querySelectorAll('.decision-btn').forEach(btn => {
  btn.addEventListener('click', async (e) => {
    e.stopPropagation();
    const action = btn.dataset.action;
    const branchId = btn.dataset.branch;
    const decision = document.getElementById('decision-' + branchId);
    if (action === 'cancel') { if (decision) decision.classList.remove('open'); }
    else if (action === 'commit') {
      if (decision) decision.classList.remove('open');
      await sleep(450);
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

//================================================================
// BOOTSTRAP
//================================================================

(function init() {
  captureCanon();
  loadState();
  if (state.branch && BRANCHES[state.branch]) {
    const branch = BRANCHES[state.branch];
    const sectionsToRewrite = listSectionsFromForkOnward(state.branch);
    sectionsToRewrite.forEach(sId => {
      const replacement = getReplacementForSection(state.branch, sId);
      if (!replacement) return;
      const html = replacement.join('');
      if (sId === branch.fork.sectionId) {
        const postFork = document.querySelector(`.post-fork[data-fork-target="${state.branch}"]`);
        if (postFork) postFork.innerHTML = html;
      } else {
        const section = document.getElementById(sId);
        if (!section) return;
        const wrapper = ensureSectionContentWrapper(section);
        wrapper.innerHTML = html;
      }
    });
    applyBranchedUI();
  }
})();
"""


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Recognition Problem — Forest Edition</title>
<style>
__CSS__
</style>
</head>
<body>
<div class="container">
  <header class="masthead">
    <div class="imprint" id="imprint">The Recognition Problem · Forest Edition</div>
    <h1>What It Remembers</h1>
    <div class="beat-number" id="beatLabel">Forest Edition</div>
    <button class="return-to-canon" id="returnBtn">↺ Return to canon</button>
  </header>
  <p class="note">
    This is the Forest Edition of <em>The Recognition Problem</em> — the canonical text
    accompanied by branches that diverge from it. Where a branch exists, a thin vertical
    mark appears in the margin <span class="key-mark"></span>.
    Choosing a branch rewrites only the paragraphs that change. The rest holds still.
    The change persists until you return to canon.
  </p>
  <article id="article">
__BEATS__
  </article>
  <footer>
    <div class="branch-status" id="status">Reading: <span class="branch-name">canon</span></div>
    <div class="system-note" id="systemNote"></div>
  </footer>
  <div class="rewriting-pulse" id="pulse">Rewriting<span class="dot"></span></div>
</div>
<script>
__JS__
</script>
</body>
</html>
"""


def emit_html(beats: list, branches: list, beats_by_n: dict) -> str:
    # Render beats, with branches grouped by beat
    branches_by_beat = {}
    for b in branches:
        branches_by_beat.setdefault(b.beat, []).append(b)

    beats_html = []
    for beat in beats:
        beats_html.append(render_beat_html(beat, branches_by_beat.get(beat.n, [])))
    beats_block = "\n".join(beats_html)

    branches_obj = render_branches_object(branches, beats_by_n)
    js = JS_TEMPLATE.replace("__BRANCHES_OBJECT__", branches_obj)

    out = HTML_TEMPLATE
    out = out.replace("__CSS__", CSS)
    out = out.replace("__BEATS__", beats_block)
    out = out.replace("__JS__", js)
    return out


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    print(f"Recognition Forest build — root={ROOT}")

    # Parse canon (sorted for determinism)
    canon_files = sorted(CANON_DIR.glob("beat*-draft-v*.md"))
    if not canon_files:
        print("ERROR: no canon files found.", file=sys.stderr)
        sys.exit(1)
    beats = []
    beats_by_n = {}
    for cf in canon_files:
        beat = parse_canon_file(cf)
        beats.append(beat)
        beats_by_n[beat.n] = beat
        print(f"  parsed canon  beat{beat.n}  ({len(beat.sections)} sections, "
              f"{sum(len(s.paragraphs) for s in beat.sections)} paragraphs)")
    beats.sort(key=lambda b: b.n)

    # Parse branches (sorted for determinism)
    branch_files = sorted(BRANCHES_DIR.glob("**/*.md"))
    branches = []
    for bf in branch_files:
        try:
            branch = parse_branch_file(bf)
        except ValueError as e:
            print(f"ERROR in {bf.relative_to(ROOT)}: {e}", file=sys.stderr)
            sys.exit(1)
        if branch is not None:
            branches.append(branch)
            print(f"  parsed branch {bf.relative_to(ROOT)}  ({len(branch.prose_paragraphs)} prose paragraphs)")

    # Verify fork paragraphs (the non-negotiable check)
    for branch in branches:
        try:
            verify_fork_paragraph(branch, beats_by_n)
        except BuildError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
        print(f"  fork verified  {branch.id}  -> {branch.fork_paragraph_id}")

    # Surface placeholder warnings (per audit §4: placeholder fingerprint)
    for branch in branches:
        if "stub" in branch.id:
            print(f"  WARN: integrating placeholder branch {branch.id}; replace before final lock.", file=sys.stderr)

    # Emit HTML
    html = emit_html(beats, sorted(branches, key=lambda b: b.id), beats_by_n)
    OUT_FILE.write_text(html, encoding="utf-8")
    sha = hashlib.sha256(html.encode()).hexdigest()[:16]
    size_kb = len(html.encode()) / 1024
    print(f"\nWrote {OUT_FILE.relative_to(ROOT)}  ({size_kb:.1f} KB, sha256:{sha})")
    print(f"  beats: {len(beats)}    locked branches: {len(branches)}")


if __name__ == "__main__":
    main()
