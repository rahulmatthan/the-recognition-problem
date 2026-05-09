# Branch Markdown Template

Every branch lives at `branches/beat<N>/<branch-id>.md` and follows this structure exactly. The `branch-drafter` agent uses this template; the `build-engineer` parses it.

```markdown
---
id: bN-slug                          # e.g., b6-reset
beat: N                              # 1-10
title: Branch Name                   # human-readable
summary: One short sentence for decision card  # 15-30 words; evocative, no spoilers
fork_at: |                           # exact paragraph from canon, character-for-character
  [the fork paragraph, in its entirety]
type: Local                          # or "Local + terminal-eligible"
length_target: ~XXXX words           # from ledger §5.4
status: Draft v1                     # Draft v1 | In voice review | In arch review | In coda review | Pending Rahul | Locked
---

# Branch: [Title]

## Branch prose

[The substitute material from the fork forward. This is what the build script uses to replace canon paragraphs from the fork forward.]

[If the branch includes a Tchaikovsky-register coda, it goes here in italic markdown after a horizontal rule.]

---

*[Coda in italic if applicable. Beat 1 and Beat 7 branches do not have codas.]*

---

## Drafting notes

- **Voice anchors held:** [which sentences from the canon's voice you tracked]
- **Architectural threads preserved:** [which of the §A and §B threads from architectural-threads.md]
- **Signature image:** [what replaces canon's signature image]
- **Coda implication addressed:** [what this branch's coda does to the category's defining feature, per ledger Part 6]
- **Difficulties:** [anything that pushed back during drafting]

## Self-review

[One paragraph from the drafter for reviewers: what to look at, what was hardest, anything you're uncertain about.]

## Review log

[Reviewers append here. Empty initially.]
```

# Frontmatter field rules

- **`id`:** the canonical branch ID from `ledger.md` §3 (e.g., `b1-carsick`, `b5-reset`, `b10-lie`).
- **`beat`:** integer 1–10.
- **`title`:** human-readable name; matches `ledger.md` §3.
- **`summary`:** one short sentence describing the branch's effect, in evocative-not-spoiling form. Used by the decision card UI when the reader hovers/clicks the marginal mark. Aim for 15–30 words. Required from b1-walk forward.
- **`fork_at`:** the exact paragraph from canon that is the **last shared with the branch** — i.e., the paragraph immediately *before* the branch's first divergent paragraph. The build splices on this match: canon is preserved up through and including this paragraph, then the branch's prose replaces the next paragraph onward. **Character-for-character match required.** A YAML pipe (`|`) preserves the paragraph as a multi-line literal. A single missing word breaks the build.

  *Example (b2-kano, 2026-05-03):* the ledger §6 entry says "fork at 'Adaeze closed her eyes'", but "Adaeze closed her eyes" is the first sentence of the paragraph the branch *replaces* (canon's Kano confession). The actual `fork_at` value is the paragraph *immediately before* — Ajani's two-word line "Go ahead." That's the last shared paragraph; canon's "Adaeze closed her eyes…" begins the divergent section. b1-walk follows the same convention (the ledger says "After Maya's beach reply"; the `fork_at` is Maya's full line).

  When the ledger's "fork at X" describes the *point* of divergence rather than naming the last-shared paragraph itself, the drafter resolves by reading canon and using the immediately-prior paragraph as `fork_at`.
- **`type`:** `Local` for most branches; `Local + terminal-eligible` for `b5-reset` only (and possibly others as identified later).
- **`length_target`:** the target word count from `ledger.md` §5.4. Tolerance ±20%; surface to Rahul if the branch wants to be much longer/shorter.
- **`status`:** advances through the workflow. Locked branches are integrated by the build.

# Branch prose section rules

- **Do not include canon paragraphs before the fork.** The build script splices canon in. Your file contains only the substitute material.
- **The fork paragraph itself is *not* in the prose section** — it is in the frontmatter. The branch picks up *immediately after* the fork.
- The coda goes after the chapter prose, separated by a horizontal rule, in italic markdown.

# Status progression

```
Draft v1
 → In voice review (voice-continuity-checker working)
 → In arch review (architectural-consistency-checker working)
 → In coda review (coda-specialist working) — skipped for Beat 1 and Beat 7
 → Pending Rahul (orchestrator presents)
 → Locked (orchestrator updates ledger; build-engineer integrates)
```

A SEND BACK from any reviewer returns the branch to `Draft vN+1` and the cycle restarts.
