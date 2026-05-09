# Agent Roster — Recognition Forest

This is the human-readable description of the agents defined in `.claude/agents/`. Use this as the orientation document; the system prompts are the source of truth.

There are 9 agents: 4 creative, 5 engineering. Coordination work (status tracking, ledger maintenance, decision surfacing) is handled directly by the orchestrator (the main Claude Code session), not by a subagent.

---

## Creative agents

### `branch-drafter`
- **Job:** Write the prose of a single branch chapter.
- **Reads:** `ledger.md` (especially the branch's Part 6 entry), `process/voice-profile.md`, `process/architectural-threads.md`, `canon/beat<N>-draft-vN.md`, `process/branch-template.md`.
- **Produces:** A markdown file at `branches/beat<N>/<branch-id>.md` with frontmatter, prose, drafting notes, self-review, and an empty review log.
- **Does not:** Edit other branches. Edit canon. Run reviews. Write codas it isn't sure of (hands off to `coda-specialist`).
- **Spawn rule:** One drafter per branch. Never one drafter for multiple branches.

### `voice-continuity-checker`
- **Job:** Read a branch draft against canon and the voice profile. Return specific notes on voice drift.
- **Reads:** `process/voice-profile.md`, the canon chapter, the branch draft.
- **Produces:** An appended review section in the branch's `## Review log`.
- **Authority:** SEND BACK if voice drift is structural.
- **Does not:** Edit branch prose. Run the architectural check.

### `architectural-consistency-checker`
- **Job:** Verify a branch respects ledger §4 threads + the additional threads in `process/architectural-threads.md` + the signature image rule (folded in) + story divergence (added 2026-05-03).
- **Reads:** `ledger.md` §4 + §2.6 + §2.1, `process/architectural-threads.md`, the canon chapter, the branch draft.
- **Produces:** An appended review section in the branch's `## Review log`. Runs the §D 12-item checklist.
- **Authority:** SEND BACK on FAIL of items 1–5 (ledger §4 hardcore threads) **and item 12 (story divergence — the b2-kano failure mode)**. FLAG on items 6–11.
- **Does not:** Edit branch prose. Check voice. Check coda prose quality.

### `coda-specialist`
- **Job:** Draft Tchaikovsky-register codas (the italic anomaly-log entries) when a branch is missing one. Review codas drafted by `branch-drafter`.
- **Reads:** `ledger.md` §4.1 + §4.4 + the branch's Part 6 entry, `process/voice-profile.md` §4, the canon chapter's coda, the branch draft.
- **Produces:** Either a coda inserted into the branch markdown, or a coda review appended to `## Review log`.
- **Knows:** The 11ms curve through eight points cold. The category's defining-feature progression cold.
- **Does not:** Write chapter prose. Change the 11ms duration. Add codas to Beat 1 or Beat 7 branches (those don't get codas).

---

## Engineering agents

### `build-engineer`
- **Job:** Owns `build/build.py` and the markdown→HTML pipeline that produces `build/recognition-problem.html`.
- **Reads:** `prototype/index-v4.html`, `ledger.md` §1.2 + §8.5, `process/branch-template.md`, `canon/`, `branches/`.
- **Produces:** The build script and the Forest Edition HTML.
- **Critical responsibility:** Verifies the fork-at paragraph in every branch matches canon character-for-character. Build fails on mismatch.
- **Does not:** Edit prose. Run reviews. Decide UI changes alone.

### `html-css-architect`
- **Job:** HTML structure and CSS — typography, layout, left-sidebar TOC, subtle canon-vs-branch shading, marginal marks, decision cards.
- **Reads:** `prototype/index-v4.html`, `ledger.md` §1.2 + §2.
- **Constraints from Rahul:** subtle canon-vs-branch visual difference; left sidebar TOC; better branch signifiers; reading-mode-vs-branch-mode signaling felt not announced; canon is default; one click back to canon always.
- **Does not:** Write JS state machine. Write animation logic. Unilaterally redesign — UX iteration goes through Rahul.

### `animation-engineer`
- **Job:** Split-flap animation, diff-aware paragraph rewriting, cascading overlap, scroll-to-first-changed-paragraph.
- **Reads:** `prototype/index-v4.html`, `ledger.md` §1.2.
- **Performance target:** 60fps on a modest laptop. Diff-aware — only changed paragraphs animate.
- **Does not:** Change branch prose. Own marginal mark visuals or decision cards.

### `branch-logic-engineer`
- **Job:** JS state machine for branch selection, localStorage persistence, decision cards, marginal mark click behaviour, reset action.
- **State:** `{branch: bN | null}` in localStorage. States: `canon | transitioning | branch_<id>`.
- **Hard rule:** One branch active at a time. Switching dynamic: select a branch (other marks hide); reset to canon (marks reappear); select B. Two explicit user intents. (Decision D, 2026-05-03.)
- **Does not:** Author animation rendering. Change prose or canon. Own UI styling.

### `prototype-tester`
- **Job:** End-to-end verification after each build. Reports findings. Does not fix.
- **Reads:** `STATUS.md`, the build output.
- **Produces:** A test run section appended to `STATUS.md` per integration.
- **Does not:** Fix bugs. Edit prose. Edit `build.py`. Soften verdicts.

---

## Coordination — handled directly by orchestrator

The opening doc proposed three optional coordination subagents. All three are folded into the main orchestrator (the Claude Code session running this project):

- **Status tracking** — the orchestrator maintains `STATUS.md`.
- **Ledger maintenance** — the orchestrator updates `ledger.md` as branches lock.
- **Decision surfacing** — the orchestrator surfaces decisions Rahul needs to make, clearly and without padding, in chat.

Reason: these tasks benefit from cross-cutting context (knowing what's drafted, what's in review, what's locked, what's blocked) that a standalone subagent would have to re-establish on every spawn. The overhead is not worth it at the scale of 23 branches.

---

## Workflow note

How these agents work together is the subject of `process/workflow.md` (Step 1.5, forthcoming). At a glance, the per-branch sequence is:

`branch-drafter` → `voice-continuity-checker` → `architectural-consistency-checker` → `coda-specialist` (review or draft) → orchestrator presents to Rahul → on approval, ledger updated and `build-engineer` integrates.

Engineering agents work in parallel with creative agents — the website build runs alongside branch drafting, using placeholder branches initially and swapping in real branches as they lock.

---

## Tool grants

Each agent's tool grant is in its frontmatter. Summary:

| Agent | Read | Write | Edit | Bash | Notes |
|---|:-:|:-:|:-:|:-:|---|
| branch-drafter | ✓ | ✓ | ✓ | | + Grep, Glob |
| voice-continuity-checker | ✓ | | ✓ | | Edit only to append review log |
| architectural-consistency-checker | ✓ | | ✓ | | Edit only to append review log |
| coda-specialist | ✓ | ✓ | ✓ | | Drafts codas into branch files |
| build-engineer | ✓ | ✓ | ✓ | ✓ | Bash to run build |
| html-css-architect | ✓ | ✓ | ✓ | ✓ | |
| animation-engineer | ✓ | ✓ | ✓ | ✓ | |
| branch-logic-engineer | ✓ | ✓ | ✓ | ✓ | |
| prototype-tester | ✓ | ✓ | ✓ | ✓ | Write/Edit only on STATUS.md |
