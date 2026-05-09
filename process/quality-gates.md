# Quality Gates — Recognition Forest

Operational definitions of "done" for each work product. Each gate is a checklist; every item must pass.

A gate failure blocks progression. The orchestrator checks gates before advancing status; agents do not self-certify.

---

## 1 — Branch draft (status: `Pending Rahul`)

A branch can move from review to `Pending Rahul` only when **all** of these hold:

### Frontmatter
- [ ] `id` matches ledger §3 (e.g., `b1-walk`).
- [ ] `beat` is integer 1–10.
- [ ] `title` matches ledger §3.
- [ ] `fork_at` is the exact paragraph from canon, character-for-character. **Build-engineer verifies; mismatch blocks the lock step but `Pending Rahul` requires it correct here too.**
- [ ] `type` is `Local` or `Local + terminal-eligible`.
- [ ] `length_target` matches ledger §5.4.
- [ ] `status` is `Pending Rahul`.

### Prose
- [ ] Word count is within ±20% of length target. (Outside this band → orchestrator escalates to Rahul before submitting.)
- [ ] No canon paragraphs prior to the fork are included in the branch file (the build splices canon).
- [ ] Coda is present **if** beat ≠ 1 and beat ≠ 7. Coda is in italic markdown after a horizontal rule.
- [ ] No coda is present if beat = 1 or beat = 7.
- [ ] Closing image replaces the canon chapter's signature image (per ledger §2.6 and the architectural-consistency-checker's verdict).

### Reviews
- [ ] `voice-continuity-checker` has appended a review with **Verdict: PASS** (FLAGs allowed; FAILs not).
- [ ] `architectural-consistency-checker` has appended a review with **Verdict: PASS**. All §A.1–§A.5 (ledger §4 hardcore threads) at PASS — no FAILs allowed on these. §B and signature image at PASS or FLAG.
- [ ] `coda-specialist` has appended a review with **Verdict: PASS** (or branch is in Beat 1 / Beat 7).

### Authorship metadata
- [ ] `## Drafting notes` section is filled in (voice anchors, threads preserved, signature image, coda implication, difficulties).
- [ ] `## Self-review` paragraph is present.
- [ ] `## Review log` contains all required reviewer entries with verdicts.

### Presentation gate (when status moves to `Pending Rahul`)
- [ ] Orchestrator presents the **full branch prose verbatim inline** (or full diff vs canon for branches >2,000 words). Rahul reads the prose, not just metadata. See `workflow.md` §1 / "How the orchestrator presents to Rahul."

---

## 2 — Branch locked (status: `Locked`)

A branch moves from `Pending Rahul` to `Locked` only when **all** of these hold:

- [ ] Rahul has given explicit approval. ("Approved" / "lock it" / similar — not silence, not implicit).
- [ ] Frontmatter `status` is updated to `Locked` with a `locked_date: YYYY-MM-DD`.
- [ ] `ledger.md` Part 6 entry for this branch is annotated with `**Status:** Locked YYYY-MM-DD` and any final notes that emerged during drafting.
- [ ] `STATUS.md` per-branch table is updated to `Locked`.
- [ ] `build-engineer` has integrated the branch into `build/recognition-problem.html`. The build runs without errors. The fork-paragraph splice succeeds.
- [ ] `prototype-tester` has verified the integration. Specifically:
  - Marginal mark appears at the fork paragraph.
  - Decision card opens on click.
  - Branch selects cleanly.
  - Animation runs.
  - Page scrolls to first changed paragraph.
  - Branch reads to its end.
  - Reload preserves selection.
  - Reset returns to canon.
  - No console errors.

If any of the prototype-tester checks fail, the branch is **not** locked. Engineering agents fix; re-test; only then lock.

---

## 3 — Website increment (each integration)

After each branch integration:

- [ ] Build runs without errors. Output is a single self-contained HTML file.
- [ ] Animation runs at 60fps on a modest laptop profile (or with 4x CPU throttle on a desktop).
- [ ] Branch state persists across reload. localStorage holds `{branch: bN | null}`.
- [ ] No console errors or warnings.
- [ ] Selecting a branch and then resetting returns to canon with no broken references, no leftover branch DOM, no stuck animation.
- [ ] One-branch-at-a-time enforcement holds (selecting branch B while A is active goes through canon).
- [ ] Tested in Safari and Chrome at minimum.
- [ ] No external runtime dependencies. No CDN links. No external font loads (or fonts inlined).

The `prototype-tester` runs this checklist on every integration and appends results to `STATUS.md`.

---

## 4 — Project complete (Phase 2 endpoint)

The Phase 2 deliverable is complete when **all** of these hold:

### Branches
- [ ] All 23 branches at `status: Locked` in their frontmatter.
- [ ] All 23 reviewed (voice + arch + coda where applicable) with PASS verdicts on file.
- [ ] Ledger §3 table shows all 23 with lock dates.
- [ ] Ledger Part 6 entries annotated with final length and any notes that emerged in drafting.

### Website
- [ ] `build/recognition-problem.html` is a single self-contained HTML file integrating all 23 branches with the canon.
- [ ] A reader can: open the file, read canon end-to-end, click any marginal mark, choose any branch, watch the split-flap animation, read the branch to its end, return to canon, across all 23 branches in any chapter.
- [ ] State persists across reload.
- [ ] One branch active at a time, enforced.
- [ ] No console errors.
- [ ] Animation at 60fps on a modest laptop.

### Documentation
- [ ] `STATUS.md` is current.
- [ ] `CLAUDE.md` is current and explains how a future session picks up the project (where everything is, what hard rules apply, the workflow).
- [ ] `process/voice-profile.md` and `process/architectural-threads.md` reflect what was learned during the 23-branch drafting.
- [ ] `ledger.md` is current.

### Sign-off
- [ ] Rahul reads through the file end to end and confirms the Forest Edition is what he wanted to hand to a reader.

---

## 5 — Working docs (when to update)

The voice profile and architectural threads document are working layers, not deliverables. They sharpen as drafting proceeds.

### `process/voice-profile.md`
**Updated by orchestrator after each Phase 2.1 branch locks.** Specifically: after b1-walk, b8-tell, b2-kano, b7-say-no. The orchestrator reviews the reviewer notes for each, identifies any tic / anti-pattern / per-beat refinement that should be added, and appends.

In Phase 2.2 onward, updates only when reviewers catch a recurring pattern not yet documented.

### `process/architectural-threads.md`
**Updated whenever a reviewer catches a thread not yet documented**, in any phase. Append to §E (Threads that may emerge).

The ledger remains the source of truth. The working layer is where new learning lands.

### `process/decisions.md`
**Updated whenever Rahul makes a non-trivial decision** that future drafters / reviewers should know about. Specifically:
- Resolution of an ambiguous fork paragraph
- Approval / rejection of a UX/UI proposal
- Length-target deviation accepted
- Voice profile change
- Workflow change

The decisions log lets future sessions reconstruct *why* something is the way it is.

---

## 6 — Gate enforcers (who checks what)

| Gate | Checked by |
|---|---|
| Frontmatter complete | Orchestrator before submitting to Rahul |
| Word count in band | Orchestrator |
| Fork paragraph exact match | `build-engineer` (build-time) + orchestrator (pre-submit) |
| Coda present where required | `coda-specialist` + orchestrator |
| Voice review PASS | `voice-continuity-checker` |
| Arch review PASS on §A.1–§A.5 | `architectural-consistency-checker` |
| Signature image replaced | `architectural-consistency-checker` (item 11) |
| Rahul approval recorded | Orchestrator |
| Ledger updated on lock | Orchestrator |
| STATUS.md updated on lock | Orchestrator |
| Build integration succeeds | `build-engineer` |
| End-to-end verification | `prototype-tester` |
| Performance at 60fps | `prototype-tester` |
| All 23 locked at Phase 2 end | Orchestrator |

---

## 7 — Cycle accounting

The orchestrator tracks per-branch in `STATUS.md`:
- Date drafting started
- Number of drafts (v1, v2, ...)
- Date each review completed
- Date locked

If average drafts-per-branch climbs above 2 across the first 4 branches (Phase 2.1), the orchestrator flags this to Rahul as a signal that the agent prompts may need refinement before Phase 2.2 begins.
