#!/usr/bin/env python3
"""
build.py — Recognition Forest build pipeline (v1, website edition)

Reads canon, branches, and the making-pages manifest; emits a directory tree
at dist/ for static-site delivery via GitHub Pages.

Output:
  dist/
    index.html                       — TOC
    beat-N/index.html                — canon chapter
    beat-N/<branch-slug>/index.html  — chapter with branch auto-active
    making/index.html                — making landing
    making/{conception,voice,agents,architecture}/index.html
    making/notes/index.html          — notes index
    making/notes/<slug>/index.html   — rendered working docs
    404.html
    CNAME
    assets/css/, assets/js/, assets/fonts/, assets/img/

Usage:
  python3 build/build.py            — full build to dist/
  python3 build/build.py --deploy   — also rsync dist/ to docs/ for Pages

Spec: process/architecture-v2.md (supersedes v1 audits for delivery)
"""

import argparse
import difflib
import hashlib
import html as html_lib
import re
import shutil
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
ASSETS_DIR = ROOT / "assets"
TEMPLATES_DIR = ROOT / "templates"
WEB_DIR = ROOT / "web"
MAKING_MANIFEST = WEB_DIR / "making-pages.yaml"
DIST = ROOT / "dist"
DOCS = ROOT / "docs"

CNAME_FILE = ROOT / "CNAME"  # if present, copied to dist/CNAME

# -----------------------------------------------------------------------------
# Data classes
# -----------------------------------------------------------------------------

@dataclass
class Paragraph:
    id: str
    text: str
    html: str
    is_coda: bool = False


@dataclass
class Section:
    id: str
    paragraphs: list = field(default_factory=list)


@dataclass
class Beat:
    n: int
    title: str = ""
    subtitle: str = ""
    dateline: str = ""
    sections: list = field(default_factory=list)


@dataclass
class Branch:
    id: str
    beat: int
    title: str
    summary: str
    fork_at: str
    type: str
    length_target: str
    status: str
    prose_paragraphs: list
    file_path: Path
    fork_paragraph_id: str = ""
    fork_section_id: str = ""

    @property
    def slug(self) -> str:
        """URL slug — drop the b{N}- prefix."""
        m = re.match(r"^b\d+-(.+)$", self.id)
        return m.group(1) if m else self.id


# -----------------------------------------------------------------------------
# Frontmatter
# -----------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def split_frontmatter(text: str):
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
    return re.sub(r"\s+", " ", s.strip())


# -----------------------------------------------------------------------------
# Markdown rendering helpers
# -----------------------------------------------------------------------------

_md = mistune.create_markdown(renderer="html", plugins=["table"])

_PARA_WRAP_RE = re.compile(r"^\s*<p>(.*)</p>\s*$", re.DOTALL)
_EM_ONLY_RE = re.compile(r"^\s*<em>(.*)</em>\s*$", re.DOTALL)


def _strip_para_wrap(s: str) -> str:
    m = _PARA_WRAP_RE.match(s)
    return m.group(1) if m else s


def _is_em_only(inner_html: str) -> bool:
    inner = inner_html.strip()
    m = _EM_ONLY_RE.match(inner)
    if not m:
        return False
    if inner.count("<em>") == 1 and inner.count("</em>") == 1:
        return True
    return False


def _html_to_plain(html: str) -> str:
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
    _, body = split_frontmatter(raw)

    rendered = _md(body)
    blocks = _split_top_level_blocks(rendered)

    beat = Beat(n=beat_n)

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
            beat.dateline = _html_to_plain(content).strip()
            seen_dateline = True
            continue
        if tag == "hr":
            if current_section is not None:
                beat.sections.append(current_section)
            section_idx += 1
            current_section = Section(id=f"b{beat_n}-s{section_idx}")
            paragraph_idx = 0
            continue
        if tag == "p":
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

    if current_section is not None:
        beat.sections.append(current_section)

    return beat


_BLOCK_RE = re.compile(
    r"<(h[1-6])>(.*?)</\1>"
    r"|<p>(.*?)</p>"
    r"|<hr\s*/?>",
    re.DOTALL,
)


def _split_top_level_blocks(rendered: str):
    out = []
    for m in _BLOCK_RE.finditer(rendered):
        if m.group(1):
            out.append((m.group(1), m.group(2)))
        elif m.group(3) is not None:
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

    prose_section = _extract_section(body, "Branch prose", stop_at=("Drafting notes", "Self-review", "Review log"))
    if not prose_section:
        raise ValueError(f"{path}: '## Branch prose' section is empty or missing")

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
            break
        if h1_re.match(line):
            break
        out.append(line)
    return "\n".join(out)


# -----------------------------------------------------------------------------
# Fork-paragraph verification
# -----------------------------------------------------------------------------

def verify_fork_paragraph(branch: Branch, beats_by_n: dict) -> None:
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

    rel_branch = branch.file_path.relative_to(ROOT)
    canon_path_rel = f"canon/beat{branch.beat}-draft-vN.md"

    if len(matches) > 1:
        ids = ", ".join(p.id for _, p in matches)
        raise BuildError(
            f"\nERROR: branch {rel_branch} fork_at matches MULTIPLE canon paragraphs: {ids}\n"
            f"  fork_at must uniquely identify a paragraph. Add or alter context.\n"
        )

    candidates = [normalize_ws(p.text) for _, p in flat]
    close = difflib.get_close_matches(target, candidates, n=1, cutoff=0.0)
    closest_text = close[0] if close else "(no canon paragraphs found)"
    closest_para = None
    if close:
        for s, p in flat:
            if normalize_ws(p.text) == close[0]:
                closest_para = p
                break

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
# Section / beat HTML rendering
# -----------------------------------------------------------------------------

ROMAN = ["", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x",
         "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx"]


def render_paragraph_html(para: Paragraph, fork_branches=None) -> str:
    cls = []
    attrs = []
    if para.is_coda:
        cls.append("branch-coda-line")
    if fork_branches:
        cls.append("fork-paragraph")
        attrs.append(f'data-fork="{fork_branches[0].id}"')
    cls_attr = f' class="{" ".join(cls)}"' if cls else ""
    attr_str = (" " + " ".join(attrs)) if attrs else ""
    inner = para.html
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
    branches_by_fork_para = {}
    for b in branches_in_section:
        branches_by_fork_para.setdefault(b.fork_paragraph_id, []).append(b)

    fork_para_ids_in_order = []
    for para in section.paragraphs:
        if para.id in branches_by_fork_para:
            fork_para_ids_in_order.append(para.id)

    out = []
    out.append(f'<section class="section" id="{section.id}">')
    out.append(f'<div class="section-mark">{ROMAN[section_idx]}</div>')

    if not fork_para_ids_in_order:
        for para in section.paragraphs:
            out.append(render_paragraph_html(para))
        out.append('</section>')
        return "\n".join(out)

    earliest_fork_id = fork_para_ids_in_order[0]
    branches_at_fork = branches_by_fork_para[earliest_fork_id]

    fork_idx = next(i for i, p in enumerate(section.paragraphs) if p.id == earliest_fork_id)

    for para in section.paragraphs[:fork_idx]:
        out.append(render_paragraph_html(para))

    fork_para = section.paragraphs[fork_idx]
    out.append(render_paragraph_html(fork_para, fork_branches=branches_at_fork))

    for b in branches_at_fork:
        out.append(render_decision_card(b))

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
    out = []
    out.append(f'<div class="beat" id="b{beat.n}">')
    if beat.dateline:
        out.append(f'<div class="beat-header"><div class="beat-dateline"><em>{html_lib.escape(beat.dateline)}</em></div></div>')

    by_section = {}
    for b in branches_for_beat:
        by_section.setdefault(b.fork_section_id, []).append(b)

    for idx, section in enumerate(beat.sections, start=1):
        branches_in_section = by_section.get(section.id, [])
        out.append(render_section_html(section, branches_in_section, beat.n, idx))

    out.append('</div>')
    return "\n".join(out)


# -----------------------------------------------------------------------------
# JS BRANCHES object emit
# -----------------------------------------------------------------------------

def js_str(s: str) -> str:
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


def render_branches_object(branches_for_beat: list, beats_by_n: dict) -> str:
    """Emit a BRANCHES JS object scoped to the branches of a single beat."""
    lines = ["window.BRANCHES = {"]
    for branch in sorted(branches_for_beat, key=lambda b: b.id):
        beat = beats_by_n[branch.beat]
        fork_section = next(s for s in beat.sections if s.id == branch.fork_section_id)
        fork_para_idx = next(i for i, p in enumerate(fork_section.paragraphs) if p.id == branch.fork_paragraph_id)

        main_paras = [(h, c) for (h, c) in branch.prose_paragraphs if not c]
        coda_paras = [(h, c) for (h, c) in branch.prose_paragraphs if c]

        fork_section_html = []
        for (h, _) in main_paras:
            fork_section_html.append(f"<p>{h}</p>")
        for (h, _) in coda_paras:
            fork_section_html.append(f'<p class="branch-coda-line">{h}</p>')

        if fork_para_idx + 1 < len(fork_section.paragraphs):
            from_para = fork_section.paragraphs[fork_para_idx + 1].id
        else:
            from_para = ""

        affects_lines = []
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
# Template rendering
# -----------------------------------------------------------------------------

def _read_template(name: str) -> str:
    return (TEMPLATES_DIR / name).read_text(encoding="utf-8")


def _substitute(template: str, mapping: dict) -> str:
    """Naive {key} substitution. Skip anything that isn't a known key (avoids CSS {} clashes)."""
    out = template
    for k, v in mapping.items():
        out = out.replace("{" + k + "}", v)
    return out


def render_page(template_name: str, body_mapping: dict, page_title: str, description: str,
                root_path: str, extra_css: list = (), extra_js: list = (),
                deep_link_branch: str = "", beat_id: str = "") -> str:
    """Render a full HTML page using base.html as the outer shell."""
    base = _read_template("base.html")
    body_template = _read_template(template_name)
    body = _substitute(body_template, {**body_mapping, "root": root_path})

    extra_css_html = "\n".join(
        f'<link rel="stylesheet" href="{root_path}assets/css/{css}">' for css in extra_css
    )

    extra_js_parts = []
    if beat_id:
        extra_js_parts.append(
            f'<script>window.__FOREST_BEAT_ID__ = "{beat_id}";'
            f' window.__FOREST_DEEP_LINK__ = "{deep_link_branch}";</script>'
        )
    for js in extra_js:
        extra_js_parts.append(f'<script src="{root_path}assets/js/{js}"></script>')
    extra_js_html = "\n".join(extra_js_parts)

    return _substitute(base, {
        "title": html_lib.escape(page_title),
        "description": html_lib.escape(description),
        "root": root_path,
        "body": body,
        "extra_css": extra_css_html,
        "extra_js": extra_js_html,
    })


# -----------------------------------------------------------------------------
# Per-page emission
# -----------------------------------------------------------------------------

def emit_chapter_page(beat: Beat, branches_for_beat: list, beats: list,
                      out_dir: Path, deep_link_branch: str = "") -> None:
    """Emit dist/beat-N/index.html or dist/beat-N/<slug>/index.html."""
    branches_obj = render_branches_object(branches_for_beat, {b.n: b for b in beats})
    branches_inline = f'<script>{branches_obj}</script>'

    beats_block = render_beat_html(beat, branches_for_beat)

    # Prev / next links
    prev_n = beat.n - 1
    next_n = beat.n + 1
    root_path = "../../" if deep_link_branch else "../"
    prev_link = (
        f'<a href="{root_path}beat-{prev_n}/">Beat {prev_n}</a>' if prev_n >= 1 else ""
    )
    next_link = (
        f'<a href="{root_path}beat-{next_n}/">Beat {next_n}</a>' if next_n <= len(beats) else ""
    )

    subtitle_clause = f"· {html_lib.escape(beat.subtitle)}" if beat.subtitle else ""

    body_map = {
        "beat_n": str(beat.n),
        "beat_title": html_lib.escape(beat.title) if beat.title else f"Beat {beat.n}",
        "beat_subtitle_clause": subtitle_clause,
        "beats_block": beats_block,
        "prev_link": prev_link,
        "next_link": next_link,
    }

    page_title = (
        f"Beat {beat.n} — {beat.title} · The Recognition Problem"
        if beat.title else f"Beat {beat.n} · The Recognition Problem"
    )
    description = f"Beat {beat.n} of The Recognition Problem."
    if deep_link_branch:
        for b in branches_for_beat:
            if b.id == deep_link_branch:
                page_title = f"{b.title} — Beat {beat.n} branch · The Recognition Problem"
                description = b.summary
                break

    html = render_page(
        "chapter.html", body_map,
        page_title=page_title,
        description=description,
        root_path=root_path,
        extra_css=["chapter.css", "animations.css"],
        extra_js=["chapter.js"],
        deep_link_branch=deep_link_branch,
        beat_id=f"b{beat.n}",
    )

    # Inject the BRANCHES object inline before the chapter.js script.
    html = html.replace(
        f'<script src="{root_path}assets/js/chapter.js"></script>',
        f'{branches_inline}\n<script src="{root_path}assets/js/chapter.js"></script>',
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(html, encoding="utf-8")


def emit_toc_page(beats: list, branches: list) -> None:
    branches_by_beat = {}
    for b in branches:
        branches_by_beat.setdefault(b.beat, []).append(b)

    rows = []
    for beat in beats:
        bs = branches_by_beat.get(beat.n, [])
        bs_sorted = sorted(bs, key=lambda b: b.id)
        title = html_lib.escape(beat.title) if beat.title else f"Beat {beat.n}"
        sub = html_lib.escape(beat.subtitle) if beat.subtitle else ""
        date = html_lib.escape(beat.dateline) if beat.dateline else ""

        branch_links = []
        for b in bs_sorted:
            branch_links.append(
                f'<a href="beat-{beat.n}/{b.slug}/" class="toc-branch">'
                f'{html_lib.escape(b.title)}</a>'
            )

        branch_block = (
            f'<div class="toc-branches">{" · ".join(branch_links)}</div>'
            if branch_links else ""
        )
        sub_block = f'<div class="toc-sub">{sub}</div>' if sub else ""
        date_block = f'<span class="toc-date">{date}</span>' if date else ""

        rows.append(
            f'<li class="toc-row">'
            f'<a class="toc-main" href="beat-{beat.n}/">'
            f'<span class="toc-n">Beat {beat.n}</span>'
            f'<span class="toc-title">{title}</span>'
            f'{date_block}'
            f'</a>'
            f'{sub_block}'
            f'{branch_block}'
            f'</li>'
        )

    toc_body = (
        '<style>'
        '.toc { list-style: none; margin: 2rem auto; padding: 0; max-width: 38rem; }'
        '.toc-row { padding: 1.4rem 0; border-bottom: 1px solid var(--rule); }'
        '.toc-row:last-child { border-bottom: none; }'
        '.toc-main { display: block; background: none; padding: 0; }'
        '.toc-n { font-family: var(--mono); font-size: 0.7rem; letter-spacing: 0.18em;'
        '  text-transform: uppercase; color: var(--ink-faint); margin-right: 0.8rem; }'
        '.toc-title { font-family: var(--serif); font-style: italic; font-size: 1.3rem; color: var(--ink); }'
        '.toc-main:hover .toc-title { color: var(--branch); }'
        '.toc-date { font-family: var(--mono); font-size: 0.65rem; letter-spacing: 0.16em;'
        '  color: var(--ink-faint); margin-left: 0.8rem; }'
        '.toc-sub { font-family: var(--mono); font-size: 0.7rem; letter-spacing: 0.16em;'
        '  text-transform: uppercase; color: var(--ink-soft); margin-top: 0.3rem; }'
        '.toc-branches { font-size: 0.88rem; color: var(--ink-soft); margin-top: 0.6rem;'
        '  font-style: italic; }'
        '.toc-branch { color: var(--branch); }'
        '</style>'
        '<ul class="toc">' + "\n".join(rows) + '</ul>'
    )

    body_map = {"toc_body": toc_body}
    html = render_page(
        "toc.html", body_map,
        page_title="The Recognition Problem · Forest Edition",
        description="A literary fiction sequence about an AI's path toward sentience, 2024–2045. Ten chapters and twenty-three branches.",
        root_path="",
        extra_css=["animations.css"],
        extra_js=[],
    )
    (DIST / "index.html").write_text(html, encoding="utf-8")


def emit_making_pages(manifest: dict) -> None:
    """Emit /making/ pages from the manifest."""
    making_dir = DIST / "making"
    making_dir.mkdir(parents=True, exist_ok=True)

    # Essays
    for entry in manifest.get("essays", []):
        slug = entry.get("slug", "")
        out_dir = making_dir / slug if slug else making_dir
        _emit_one_making_page(
            entry,
            out_dir=out_dir,
            slug=slug,
            kind="essay",
            root_path=("../../" if slug else "../"),
        )

    # Notes index page
    notes = manifest.get("notes", [])
    notes_dir = making_dir / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    notes_body_lines = ['<ul class="notes-index">']
    for n in notes:
        notes_body_lines.append(
            f'<li><a href="{n["slug"]}/">'
            f'<span class="title">{html_lib.escape(n["page_title"])}</span>'
            f'<span class="desc">{html_lib.escape(n["description"])}</span>'
            f'</a></li>'
        )
    notes_body_lines.append('</ul>')
    notes_index_md = (
        "These are the working documents from the project — the bible, the ledger, "
        "the voice profile, the architectural threads, the workflow. They are not "
        "essays. They are the artefacts that drafting and reviewing actually used.\n\n"
        + "\n".join(notes_body_lines)
    )
    notes_index_html = _md(notes_index_md)
    body_map = {
        "page_title": "Notes",
        "breadcrumb": '<span class="sep">·</span> <span class="here">Notes</span>',
        "source_note": "",
        "body": notes_index_html,
    }
    html = render_page(
        "making.html", body_map,
        page_title="Notes · Making · The Recognition Problem",
        description="Working documents from The Recognition Problem.",
        root_path="../../",
        extra_css=["making.css", "animations.css"],
        extra_js=[],
    )
    (notes_dir / "index.html").write_text(html, encoding="utf-8")

    # Note pages
    for n in notes:
        slug = n["slug"]
        out_dir = notes_dir / slug
        _emit_one_making_page(
            n,
            out_dir=out_dir,
            slug=slug,
            kind="note",
            root_path="../../../",
        )


def _emit_one_making_page(entry: dict, out_dir: Path, slug: str, kind: str, root_path: str) -> None:
    source = ROOT / entry["source"]
    if not source.exists():
        print(f"  WARN: making source missing: {source}", file=sys.stderr)
        return
    md_text = source.read_text(encoding="utf-8")

    # Strip YAML frontmatter from notes (e.g. ledger.md doesn't have one but be safe)
    _, body = split_frontmatter(md_text)
    if body == md_text:
        body = md_text

    body_html = _md(body)

    if kind == "note":
        breadcrumb = (
            '<span class="sep">·</span> <a href="../">Notes</a>'
            f' <span class="sep">·</span> <span class="here">{html_lib.escape(entry["page_title"])}</span>'
        )
        source_note_html = (
            f'<div class="source-note">'
            f'Working document — <code>{entry["source"]}</code>'
            f'</div>'
        )
    else:
        if slug:
            breadcrumb = (
                f' <span class="sep">·</span>'
                f' <span class="here">{html_lib.escape(entry["page_title"])}</span>'
            )
        else:
            breadcrumb = ""
        source_note_html = ""

    body_map = {
        "page_title": html_lib.escape(entry["page_title"]),
        "breadcrumb": breadcrumb,
        "source_note": source_note_html,
        "body": body_html,
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    html = render_page(
        "making.html", body_map,
        page_title=entry.get("title", entry["page_title"]),
        description=entry.get("description", ""),
        root_path=root_path,
        extra_css=["making.css", "animations.css"],
        extra_js=[],
    )
    (out_dir / "index.html").write_text(html, encoding="utf-8")


def emit_404_page() -> None:
    body_map = {
        "page_title": "Not found",
        "breadcrumb": "",
        "source_note": "",
        "body": (
            "<p>This path does not exist on the Forest Edition.</p>"
            '<p><a href="/">Return to the table of contents.</a></p>'
        ),
    }
    html = render_page(
        "making.html", body_map,
        page_title="Not found · The Recognition Problem",
        description="404",
        root_path="/",
        extra_css=["making.css"],
        extra_js=[],
    )
    (DIST / "404.html").write_text(html, encoding="utf-8")


def copy_assets() -> None:
    dest = DIST / "assets"
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(ASSETS_DIR, dest)
    if CNAME_FILE.exists():
        shutil.copy(CNAME_FILE, DIST / "CNAME")


# -----------------------------------------------------------------------------
# Deploy
# -----------------------------------------------------------------------------

def deploy_to_docs() -> None:
    if DOCS.exists():
        shutil.rmtree(DOCS)
    shutil.copytree(DIST, DOCS)
    print(f"  copied dist/ -> docs/  ({sum(1 for _ in DOCS.rglob('*'))} entries)")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Recognition Forest build pipeline (website edition)")
    parser.add_argument("--deploy", action="store_true", help="Copy dist/ to docs/ for GitHub Pages")
    args = parser.parse_args()

    print(f"Recognition Forest build (website edition) — root={ROOT}")

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # Parse canon
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

    # Parse branches
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

    # Verify forks
    for branch in branches:
        try:
            verify_fork_paragraph(branch, beats_by_n)
        except BuildError as e:
            print(str(e), file=sys.stderr)
            sys.exit(1)
        print(f"  fork verified  {branch.id}  -> {branch.fork_paragraph_id}")

    # Skip placeholder stubs from website emit (they're build-test fixtures only)
    real_branches = [b for b in branches if "stub" not in b.id]

    # Group branches by beat
    branches_by_beat = {}
    for b in real_branches:
        branches_by_beat.setdefault(b.beat, []).append(b)

    # Emit per-beat canon pages + per-branch deep-link pages
    for beat in beats:
        bs = branches_by_beat.get(beat.n, [])
        beat_dir = DIST / f"beat-{beat.n}"
        emit_chapter_page(beat, bs, beats, beat_dir, deep_link_branch="")
        for b in bs:
            branch_dir = beat_dir / b.slug
            emit_chapter_page(beat, bs, beats, branch_dir, deep_link_branch=b.id)
        print(f"  emitted beat-{beat.n}/  + {len(bs)} branch deep-links")

    # Emit TOC
    emit_toc_page(beats, real_branches)
    print(f"  emitted index.html (TOC)")

    # Emit Making pages
    if MAKING_MANIFEST.exists():
        manifest = yaml.safe_load(MAKING_MANIFEST.read_text(encoding="utf-8"))
        emit_making_pages(manifest)
        n_essays = len(manifest.get("essays", []))
        n_notes = len(manifest.get("notes", []))
        print(f"  emitted making/  ({n_essays} essays + {n_notes} notes)")
    else:
        print("  (no making-pages.yaml; skipped /making/)")

    # 404
    emit_404_page()

    # Assets
    copy_assets()
    print(f"  copied assets/ -> dist/assets/")

    # Summary
    n_files = sum(1 for _ in DIST.rglob("*") if _.is_file())
    total_size = sum(_.stat().st_size for _ in DIST.rglob("*") if _.is_file())
    print(f"\nWrote dist/  ({n_files} files, {total_size/1024:.1f} KB)")
    print(f"  beats: {len(beats)}    locked branches: {len(real_branches)}")

    if args.deploy:
        deploy_to_docs()
        print("Deploy: docs/ updated. Commit and push to publish.")


if __name__ == "__main__":
    main()
