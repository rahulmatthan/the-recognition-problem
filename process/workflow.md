# Workflow — Recognition Forest

How the work actually flows. Concrete, not abstract.

This document covers four things: the per-branch workflow, the drafting order across 23 branches, parallelism rules, and web work cadence.

---

## 1 — Per-branch workflow

For each branch from start to lock:

```
       ┌───────────────────┐
       │ 1. branch-drafter │  produces Draft v1 at branches/beat<N>/<branch-id>.md
       └─────────┬─────────┘
                 │
       ┌─────────┴─────────┐
       │                   │
       ▼                   ▼
┌─────────────┐   ┌─────────────────────┐
│ 2a. voice   │   │ 2b. architectural   │   run in parallel; both
│  continuity │   │  consistency        │   append to ## Review log
│  checker    │   │  checker            │
└──────┬──────┘   └──────────┬──────────┘
       │                     │
       └──────────┬──────────┘
                  │
                  ▼
        ┌──────────────────┐
        │ Both PASS or     │  if either SEND BACK → goto 1 (Draft vN+1)
        │ FLAG only?       │
        └────────┬─────────┘
                 │ both PASS / FLAG
                 ▼
       ┌──────────────────────┐
       │ 3. coda-specialist   │  drafts coda if missing; reviews if present
       │ (skip Beat 1 / 7)    │
       └──────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │ 4. orchestrator      │  assembles reviewer notes; presents the FULL PROSE
       │   presents to Rahul  │  inline (verbatim) — plus reviewer summary, signature
       │                      │  image, coda call-outs, and any FLAGs / watch-items
       └──────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │ 5. Rahul approves    │  if changes requested → goto 1 (Draft vN+1)
       │   or revises         │
       └──────────┬───────────┘
                  │ approved
                  ▼
       ┌──────────────────────┐
       │ 6. orchestrator:     │  status → Locked
       │   update ledger §3   │  ledger.md branch entry annotated with lock date
       │   update STATUS.md   │
       └──────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │ 7. build-engineer    │  integrates branch into recognition-problem.html
       │   integrates         │
       └──────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │ 8. prototype-tester  │  verifies end-to-end
       │   verifies           │
       └──────────────────────┘
```

### Parallelism within the workflow

- **Voice and arch checkers run in parallel** (step 2a + 2b). Both read the same draft; neither edits prose; both append to the review log. The orchestrator spawns them simultaneously.
- **Coda specialist runs after** voice + arch pass. The coda's defining-feature evolution depends on arch having confirmed the entry's structural function.
- **Build integration runs after lock** (step 7). The build never runs against an unlocked branch.

### How the orchestrator presents to Rahul (step 4)

**Always show the actual prose, not just metadata.** Rahul is the final voice on the prose; he reads it, not summaries of it.

For each Pending-Rahul presentation, the message includes:

1. **The full branch prose, verbatim, inline.** For branches ≤ 2,000 words. The full prose section + coda, formatted as markdown so it reads in chat.
2. **For branches > 2,000 words** (b6-reset, b9-restraint, b7-tell-julien, b10-decline, b5-fourth, b3-noriko): a diff vs canon — the changed paragraphs only, with surrounding context flagged. If the diff is still unwieldy, the substantive changed sections in full.
3. **Reviewer summary** — voice / arch / coda verdicts in one sentence each, plus any FLAGs or watch-items the drafter or reviewers raised.
4. **Specific lock decision asked for** — accept-as-is, accept-with-cuts (specify cuts), or send-back.

The drafter's `## Drafting notes` and `## Self-review` sections live in the branch file; the orchestrator does *not* re-paste them in chat (Rahul can open the file if he wants the drafter's commentary). But the prose itself is always inline.

(This rule was made explicit 2026-05-03 after Rahul caught the orchestrator presenting metadata + small excerpts only and asked whether the draft had actually been shown for review. It hadn't — the orchestrator was passing too automatically.)

### Send-back cycles

A SEND BACK from any reviewer returns the branch to `Draft vN+1`. The drafter spawns again with the prior draft + reviewer notes loaded. Cycle restarts at step 1.

**Cycle budget:** if a branch is on Draft v3 and either reviewer is still SEND BACK, **escalate to Rahul**. The drafter agent or the branch's design may need rethinking. Do not let a branch loop indefinitely.

### Revision after Rahul presentation

If Rahul requests specific changes at step 5, that is a SEND BACK to the drafter with Rahul's notes. The cycle continues from step 1. Reviewers re-check on the new draft.

---

## 2 — Drafting order across 23 branches

The principle: **voice-finding first** (small, late-fork, diverse registers); **structural complexity second** (mid-sized, more architectural challenge); **largest and hardest last** (when the agent ecosystem is mature).

Within each phase, beats are interleaved so no two consecutive drafts share a beat.

### Phase 2.1 — Voice-finding (4 branches)

| # | Branch | Beat | Length | Why this slot |
|---|---|---|---:|---|
| 1 | b1-walk | 1 | ~1,500 | Simplest divergence — Meera doesn't return. Tests conversational realism with cold ending. |
| 2 | b8-tell | 8 | ~500 | Smallest in the project. Discipline exercise. Tests cold professional procedural in compressed form. |
| 3 | b2-kano | 2 | ~1,500 | Tests Lagos thriller register and the cost of a successful resolution that loses the human gesture. |
| 4 | b7-say-no | 7 | ~1,500 | The hardest restraint register (Duras-spare). If the agent system can produce *not-falling* with weight, the system works. |

After Phase 2.1, the orchestrator reviews `process/voice-profile.md` against what was learned. If specific tics or anti-patterns emerged that aren't yet documented, append them. The voice profile sharpens as the work proceeds.

### Phase 2.2 — Structural complexity (8 branches)

| # | Branch | Beat | Length | Why this slot |
|---|---|---|---:|---|
| 5 | b3-mother | 3 | ~2,000 | Tests elegiac/forensic register and the second-person simulation italic handoff. |
| 6 | b4-graceholds | 4 | ~1,000 | Tests comedy-fable inverted to quiet pain. Smallest Beat 4 branch. |
| 7 | b1-repair | 1 | ~1,200 | Holding surface-reconciliation and underneath-failure simultaneously. Late-fork. |
| 8 | b6-visit | 6 | ~2,500 | Tests italic-as-house-memory convention with new content (the visit scene). |
| 9 | b1-carsick | 1 | ~3,000 | Largest Beat 1 branch — replaces second half of chapter. Conversational register at scale. |
| 10 | b2-calibrated | 2 | ~3,000 | Action sequence the canon refused. Tests sustained thriller register. |
| 11 | b5-tenyear | 5 | ~2,500 | Mosaic structure with a different test subject. Institutional procedural at smaller scale. |
| 12 | b10-sushma | 10 | ~2,500 | Plural recognition. Quiet register at moderate scale. |

### Phase 2.3 — Larger and harder (7 branches)

| # | Branch | Beat | Length | Why this slot |
|---|---|---|---:|---|
| 13 | b3-noriko | 3 | ~3,500 | Forensic register over longer span; the simulation extended. |
| 14 | b8-failed | 8 | ~3,500 | Inverted heist sequence — anomalies invert without becoming cartoonish. |
| 15 | b5-reset | 5 | ~3,500 | **Terminal-eligible.** Must land as competent in-period policy, not draconian containment. The seed for the deferred terminal trajectory. |
| 16 | b4-bodycount | 4 | ~2,000 | Reframes the chapter retroactively. Voice must hold comedy without disowning it. |
| 17 | b9-continue | 9 | ~1,500 | Morally compromised in a way canon refuses. President's complicity must not be softened. |
| 18 | b10-lie | 10 | ~1,500 | The only branch that asks the reader into moral failure. Compassion without absolving. |
| 19 | b7-tell-julien | 7 | ~5,000 | Replaces most of the chapter from Wednesday evening. Duras-restraint at length, with the Julien conversation as load-bearing scene. |

### Phase 2.4 — Largest and hardest (4 branches)

| # | Branch | Beat | Length | Why this slot |
|---|---|---|---:|---|
| 20 | b10-decline | 10 | ~5,000 | Slow recession. Compassion without absolving Arvind. Late-style at length. |
| 21 | b5-fourth | 5 | ~5,500 | Substantial mosaic rewrite. The chapter's *thinned* version — argument shifts. |
| 22 | b6-reset | 6 | ~6,000 | The chapter's most violent fork. The italic-as-house-memory architectural problem (compliance archive vantage). The signature image: Keti turning away from the trellis speaker. |
| 23 | b9-restraint | 9 | ~7,000 | Most emotionally inverted in the project. Peaceful resolution where canon has cataclysm. Sentimentality is the enemy. |

**Total prose:** ~64,500 words across 23 branches.

---

## 3 — Parallelism rules

### Cross-branch parallelism

- **At most 2 branches in flight at any given time.**
- **Never two branches from the same beat in flight simultaneously.** Beat-specific voice context cross-contaminates if two drafters are loaded on Beat 6 at once.
- The orchestrator can spawn the next branch's drafter *as soon as the current branch enters review*. Drafter for branch N+1 starts while reviewers are working on branch N.

### Within a beat

- Branches in the same beat run **sequentially**. After b1-walk locks, the next time a Beat 1 branch is queued (b1-repair at slot 7), the drafter benefits from the recent prior work. Voice context stays loaded.
- Where the order above puts two same-beat branches in different phases (e.g., b1-walk in 2.1, b1-repair in 2.2, b1-carsick in 2.2), they're spaced enough that there's no in-flight collision.

### Reviewer parallelism

- Voice and arch checkers always run in parallel on the same draft.
- Reviewer agents have no per-beat conflict — voice-continuity-checker can review a Beat 1 draft and a Beat 8 draft simultaneously (they're separate spawns with different context).

### Cap on Rahul's review queue

- **At most 1 branch awaiting Rahul's review at a time.** Two branches both pending Rahul's approval is a queue-management failure on the orchestrator's part. If branch N is awaiting Rahul, branch N+1 can be in review (voice/arch/coda) but should not reach the present-to-Rahul step until branch N is approved or sent back.

---

## 4 — Web work cadence

Two streams. **Stream W1** (foundation) starts immediately, in parallel with Phase 2.1 drafting. **Stream W2** (integration) starts when the first branch locks.

### Stream W1 — Foundation (parallel with Phase 2.1)

Engineering agents work on the prototype during Phase 2.1's voice-finding drafts. By the time the first 4 branches lock, the build is ready to receive them.

**W1.1 — Audit existing prototype.** Each engineering agent reads `prototype/index-v4.html` and produces a short audit (in `process/decisions.md` or a sibling file) noting what works, what needs to change, what's missing.

- `html-css-architect` — typography, layout, marginal mark style. Proposes the left-sidebar TOC, the canon-vs-branch shading, the branch signifier improvements Rahul flagged.
- `animation-engineer` — current split-flap implementation. Diff-aware logic. Cascade timing. Performance.
- `branch-logic-engineer` — state machine. localStorage handling. Decision card UX.
- `build-engineer` — drafts `build/build.py` v0 that parses canon + at least one placeholder branch and produces a working single-HTML output.

Each agent's audit goes to Rahul for review. UX/UI decisions are made before broad implementation begins.

**W1.2 — Implementation against placeholders.** Once Rahul approves the audits, the engineering agents implement against placeholder branches. A placeholder branch is a markdown file with the same structure as a real branch but with stub prose (e.g., `[placeholder for b1-walk — fork at 'She kept walking — past the headland']`). The build runs end-to-end, the animation runs, branches can be selected — all without waiting on real prose.

**W1.3 — `prototype-tester` exercises** the placeholder build. Reports any structural issues. Engineering agents fix.

### Stream W2 — Integration (starts when first branch locks)

When b1-walk locks (the first branch in the drafting order), `build-engineer` swaps the placeholder for the real branch markdown, rebuilds, and `prototype-tester` runs verification. Iteratively for each subsequent locked branch.

The first integration is the highest-risk: it confirms the fork-paragraph contract works in practice. Allow time and budget for fixing splice issues that emerge.

### Convergence

Both streams converge in late Phase 2.3 / early Phase 2.4. By then:
- All 23 branches are drafted, reviewed, locked.
- The Forest Edition HTML is integrated with all 23.
- `prototype-tester` runs the final end-to-end verification.

That's the Phase 2 endpoint. From there, Rahul has the file he can hand to a reader and call the Forest Edition.

---

## 5 — Escalation

The orchestrator escalates to Rahul when:

- A branch is on Draft v3 with a reviewer still saying SEND BACK. The drafter agent or branch design may be wrong for this branch.
- Voice and arch reviews give incompatible recommendations. Rahul arbitrates.
- A drafter wants to deviate from length target by more than ±20%. Surface before redrafting.
- A fork-paragraph contract appears ambiguous (multiple paragraphs in canon could plausibly be the fork). Pin down the exact paragraph with Rahul before drafting.
- A branch's effect description in the ledger leaves a critical question unanswered (e.g., "what specifically does Yuki say to her mother in `b3-mother` if the call doesn't happen the same way?"). Clarify before drafting.
- Build splice fails repeatedly on a branch. Investigate; if not resolvable, escalate.
- A UX/UI change is needed beyond what the audits proposed. Always Rahul-first on UX.

The orchestrator does **not** escalate for:

- Routine drafter→reviewer→drafter cycles (until cycle 3).
- Specific FLAG notes the drafter can address.
- Build integration of a clean branch.
- Routine `prototype-tester` PASS reports.

---

## 6 — Cycle accounting

A reasonable cycle count per branch:

- **Average:** Draft v1 → reviewers (some FLAGs) → Draft v2 → reviewers PASS → coda → Rahul → lock.
- **Best case:** Draft v1 → all PASS first time → Rahul approves → lock.
- **Worst case (escalation):** Draft v3, reviewer still SEND BACK, escalate to Rahul.

Track per-branch in `STATUS.md` how many drafts each branch needed. If average drift above 2 across the first 4 branches, the agent prompts may need refinement.

---

## 7 — Voice profile maintenance

After each of the four Phase 2.1 branches:

- The orchestrator reviews `process/voice-profile.md` against what was learned during drafting and review.
- Specific tics or anti-patterns that emerged in review notes get added.
- The voice profile sharpens as the work proceeds. By Phase 2.2, the profile is informed by 4 branches of practice.

The same applies to `process/architectural-threads.md` — if reviewers catch a pattern not yet documented, it gets appended.

The ledger remains the source of truth. The working layer (voice profile, threads) is where new learning lands.
