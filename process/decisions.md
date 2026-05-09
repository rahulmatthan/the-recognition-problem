# Decisions Log — Recognition Forest

Rolling log of decisions Rahul has made that future drafters / reviewers / engineers should know about. Newest entries at the top.

## Format

```
## YYYY-MM-DD — [topic]
**Decision:** [what was decided]
**Context:** [what prompted it]
**Applies to:** [which work / agents this informs]
```

---

## 2026-05-07 — Defer browser test + multi-section runtime fix to Phase 2.4
**Decision:** Hold the multi-section runtime JS fix until all 23 branches are drafted. Browser-test the full set in one Phase 2.4 batched pass.
**Diagnosis:** all five currently-locked branches (b1-walk, b1-repair, b2-kano, b8-tell, b9-continue) are terminal-shape, but the runtime's `commitBranch` only swaps paragraphs in sections present in a branch's `affects` map; canon's later sections remain visible below the branch's ending. Canon source is intact; this is a runtime-only rendering issue.
**Why deferred:** if any of the 18 remaining branches is rejoining-shape (fork → divert → return to canon mid-chapter), the fix needs different machinery; surfacing that case before designing the fix is cheaper than designing twice. Drafting is the long pole; browser tests verify UX feel, not prose.
**Applies to:** Phase 2.2/2.3 drafting continues without browser verification per branch; Phase 2.4 starts with the JS fix + a single batched browser-test pass.

## 2026-05-07 — Lock b1-repair, b2-kano, b9-continue as orchestrator-direct drafts; skip reviewers
**Decision:** Lock all three on first read after a four-failure subagent cascade made the standard drafter→voice/arch/coda pipeline unworkable. Orchestrator drafted directly inline; Rahul read prose inline; voice/arch/coda reviews explicitly skipped.
**Context:** Three drafters dispatched per Rahul's 2026-05-06 instruction; all three stalled at the 600s watchdog or hit 529 Overloaded. Recovery option A (orchestrator drafts directly) chosen and executed for all three.
**Implication:** the workflow's voice→arch→coda gate is *not* a hard lock-gate; Rahul can lock on first read when the orchestrator-direct path is in use and prose is pasted inline. This is a one-off pattern, not a new normal — when subagent drafting works, the standard gate stays.
**Applies to:** ledger Part 6 entries for the three branches; STATUS.md; future fallback if the cascade recurs.

## 2026-05-03 — Story divergence test added systemically + b2-kano ledger revised + audit of remaining branches
**Decision (1 of 3):** Add **story divergence test** to architectural-consistency-checker §D as item 12 + to branch-drafter's pre-submit tests. The test: *strip the prose of specific words; describe the chapter as a sequence of events; if parallel to canon's events with different content, the branch fails ledger §2.1.* Late-fork branches are most at risk. FAIL on item 12 is automatic SEND BACK.
**Decision (2 of 3):** **b2-kano ledger entry revised** per Rahul Decision B1 (shifted-weight option). The chapter's centre of gravity moves from the bank to the homecoming; the standoff resolves in ≤ 250 words; the chapter's prose weight (~1,250 words) is the drive home, the dinner, the kitchen solitude. The original draft is discarded. Re-draft with the revised ledger entry.
**Decision (3 of 3):** **Audit of remaining 22 branches** at `process/branch-divergence-audit.md`. Three branches at material risk (b1-repair, b2-kano, b9-continue); five DIVERGENT-OK that need verification on draft. b1-repair and b9-continue have proposed ledger revisions awaiting Rahul's approval.
**Why:** Rahul read b2-kano and identified the failure: events parallel canon with different content. Diagnosis: the system's reviewers had no test for story divergence; the test was in the ledger §2.1 design principles but not operationalized.
**Applies to:** all future drafters and reviewers; b2-kano redraft; pending b1-repair and b9-continue ledger revisions.

## 2026-05-03 — Show full prose inline when presenting to Rahul
**Decision:** When a branch reaches `Pending Rahul`, the orchestrator pastes the full prose verbatim inline in chat (or the full diff vs canon for branches >2,000 words). Reviewer notes and metadata are summarised; the prose itself is always shown.
**Why:** Rahul is the final voice on the prose, not just on metadata. The orchestrator was passing too automatically (b1-walk, b8-tell shown as small excerpts; b2-kano initially shown only as decisions without prose). Rahul caught this and asked whether the draft had actually been shown for review. It hadn't.
**Applies to:** `workflow.md` §1 step 4 (updated); `quality-gates.md` §1 (presentation gate added); all future Pending-Rahul messages.

## 2026-05-03 — Fork-paragraph convention made explicit
**Decision:** The branch frontmatter `fork_at` is the **last paragraph from canon shared with the branch** (i.e., the paragraph immediately *before* the branch's first divergent paragraph). When the ledger's "fork at X" describes the divergence *point* rather than naming the last-shared paragraph (e.g., b2-kano's "Adaeze closed her eyes" describes the point but is itself the first divergent line), the drafter resolves by using the immediately-prior canonical paragraph.
**Context:** b1-walk and b2-kano drafters both interpreted "fork at" this way correctly without explicit guidance. Encoded the convention explicitly in `branch-template.md` so future drafters don't re-derive it.
**Applies to:** `branch-template.md`; all future drafters.

## 2026-05-03 — Subagent permissions resolved
**Decision:** Add explicit allows in `.claude/settings.local.json` for `Write(/Users/rahul/Coding/recognition-forest/**)`, `Edit(/Users/rahul/Coding/recognition-forest/**)`, plus `python3`, `pip`, `wc`, `grep`, `ls`, `cat`, `mkdir` Bash commands. This unblocks spawned subagents (drafters, reviewers, engineers) so they can write/edit within the project tree without per-call permission prompts.
**Diagnosis:** `~/.claude/settings.json` allows Write only to `/Users/rahul/Coding/readwise/*`. The recognition-forest project had no Write/Edit allows in either user-global or project-local settings. Spawned subagents trigger interactive permission prompts that fail when Rahul isn't actively at the terminal — which is what happened to b8-tell drafter (twice) and b8-tell voice + arch reviewers (multiple times each).
**Context:** Rahul asked the orchestrator to investigate; orchestrator read the settings files and identified the gap.
**Applies to:** all spawned subagents from b2-kano onward.

## 2026-05-03 — b8-tell locked with surgical cuts
**Decision:** Lock b8-tell after applying the two surgical cuts identified by voice and coda reviewers (Decision option B): chapter-prose pre-empt cut; coda's "Only one of the curves knew it was a curve" overreach line cut. The drafter explicitly anticipated both as fix candidates in the self-review.
**Why option B over A:** two independent reviewers (voice, coda) flagged the same Tchaikovsky-overreach line; the drafter herself flagged both as fix candidates; the cuts are surgical and don't require a re-draft cycle; they make the branch's load-bearing architectural move land cleaner without changing it.
**Length:** ~720 final (down from ~750), still over the 600 advisory ceiling per Decision 2026-05-03 (length acceptance).
**Applies to:** `branches/beat8/b8-tell.md`, ledger annotation, build integration.

## 2026-05-03 — b8-tell length: accept 750 words
**Decision:** Accept b8-tell at 750 total words (407 prose + 343 coda) despite being 25% over the upper-band ceiling of 600. The branch's coda must do canon's structural work *plus* the recognition-by-humans argument; both can't fit in 500.
**Context:** Drafter surfaced length flag honestly per quality-gates §1. Three options presented to Rahul (accept / tighten to ~540 / cut the two-curves paragraph). Rahul chose accept.
**Implication:** ledger §5.4 length targets are advisory, not gates. Future branches whose argument requires more space can be similarly accepted with explicit Rahul approval.
**Applies to:** `b8-tell` review pipeline; future length-flag escalations.

## 2026-05-03 — b1-walk locked
**Decision:** Lock b1-walk as-is. Voice FLAGs ("forty years of one thing" near-verbatim canon repeat; tea-stall slightly long on rhythm) accepted. Both reviewers PASS.
**Applies to:** STATUS.md, ledger.md (Part 6 Beat 1 b1-walk entry annotation), build integration.

## 2026-05-03 — Output file size acceptable
**Decision:** ~500KB current build output (canon + 3 placeholders) is acceptable. Projected final size with all 23 branches integrated is ~950KB to 1MB. The 500KB advisory I gave earlier was wrong; the project's natural size is closer to 1MB.
**Applies to:** `build-engineer`, `prototype-tester` performance gates.

## 2026-05-03 — v0.5 build work parked before Phase 2.2
**Decision:** Park `build-engineer` v0.5 follow-up (downstream-effect branches that span multiple sections — currently unsupported) for after Phase 2.1 completes (4 branches drafted + locked). Required before Phase 2.2 begins, since `b3-noriko`, `b3-mother`, `b6-reset`, `b7-tell-julien` etc. need it.
**Applies to:** `build-engineer`; orchestrator (sequence in workflow).

## 2026-05-03 — Decision A: System fonts only
**Decision:** Use system fonts (no Spectral / JetBrains Mono externally loaded). Prototype must replace Google Fonts links with a system serif/mono stack.
**Caveat:** If system fonts visibly degrade the split-flap animation, revisit. Confidence is high — the animation flips characters via DOM manipulation, font-agnostic.
**Context:** W1 html-css audit flagged Google Fonts external load as violation of the self-contained-HTML rule.
**Applies to:** `html-css-architect`; `prototype/index-v4.html` implementation.

## 2026-05-03 — Decision B: Add `summary:` field to branch frontmatter
**Decision:** Add `summary:` field to branch frontmatter (one short sentence used by the decision card UI). Backfill into b1-walk now; required for all future branches.
**Context:** Build engineer flagged that the decision card needs a per-branch summary; auto-generating from `title` would be lossy.
**Applies to:** `process/branch-template.md`, `branch-drafter` agent prompt, `build-engineer`, all branch markdown files going forward.

## 2026-05-03 — Decision C: Placeholder branches approved
**Decision:** Approve `build-engineer` creating three `b1-stub-*` placeholder branches with `status: Locked` for W1 end-to-end testing. Placeholders to be deleted once real branches replace them.
**Context:** W1 build audit recommendation; allows the build pipeline to run end-to-end during W1 without waiting on real branch drafts.
**Applies to:** `build-engineer`; placeholders in `branches/beat1/b1-stub-*.md`.

## 2026-05-03 — Decision D: Switch dynamic — reset-then-select, not A→B chain
**Decision:** No A→B chain animation. Selecting a branch hides the other marginal marks (the reader is in the branch). Reset returns to canon and the marks become visible again. To select a different branch, the reader resets first. Two explicit user intents.
**Reverses:** earlier wording in `branch-logic-engineer.md` and `animation-engineer.md` that documented A→B chained through canon as a single user intent. Both prompts updated 2026-05-03.
**Context:** W1 animation + branch-logic audits flagged the existing prototype's behaviour as a "contract gap" — but the contract was wrong, not the prototype. The simpler model is the right one.
**Applies to:** `animation-engineer`, `branch-logic-engineer`, `agent-roster.md`, all engineering work.

## 2026-05-03 — Decision E: UX implementation specifics
**E1 — Drawer-style left sidebar TOC.** Closed by default. Opens on hover. State-persisted. Indicates visited chapters and selected branches.
**E2 — Canon-vs-branch shading via paper temperature shift.** Approved (warm canon → cool branch + 2px ochre rule on rewritten paragraphs per `html-css-architect`'s proposal in audit-html-css.md).
**E3 — No terminal-eligible marginal mark differentiation.** Per ledger §2.5 (bend, don't break) — terminal-eligible branches do not announce themselves to the reader. Reader discovers downstream impact, not upstream signaling.
**Applies to:** `html-css-architect`; `prototype/index-v4.html` implementation.

## 2026-05-03 — Folder structure

**Decision:** Approved folder structure per `CLAUDE.md` map. Renamed `recognition-forest-ledger.md` → `ledger.md`. Bible v23 lives in `bible/`. Existing prototype `index-v4.html` lives in `prototype/`.
**Context:** Step 1.2.
**Applies to:** All agents — file paths.

## 2026-05-03 — UX/UI iteration goes through Rahul

**Decision:** Engineering agents (especially `html-css-architect`) audit the existing prototype and propose UX changes. Rahul reviews and decides. Implementation only proceeds after approval.

Specific things Rahul wants reviewed:
- Better signifiers for branches.
- A left-sidebar table of contents for easy chapter access.
- Subtle shading / visual signifiers for chapters that have branched, so the reader knows when they are on canon and when on a branch.

**Context:** Step 1.2 Q3. Rahul flagged that he wants to spend time on UX/UI separately.
**Applies to:** `html-css-architect`, `branch-logic-engineer`, `prototype-tester`, orchestrator (do not unilaterally change UX).

## 2026-05-03 — Agent roster: 9 agents, voice/arch separate, signature-image folded

**Decision:** 9 agents (4 creative, 5 engineering). `voice-continuity-checker` and `architectural-consistency-checker` remain separate (different reference docs, different focused attention). `signature-image-checker` folded into `architectural-consistency-checker` as item 11 of the §D checklist. Coordination handled by orchestrator directly (no project-status-tracker subagent).
**Context:** Step 1.4 Qs A and B.
**Applies to:** Workflow, future spawning decisions.
