# CLAUDE.md — Recognition Forest

Entry point for any Claude Code session on this project. Read this first.

## What this project is

The Recognition Forest is the digital companion to *The Recognition Problem*, Rahul Matthan's literary fiction sequence tracing an AI's path toward sentience across 2024–2045. Two parallel deliverables:

1. **23 branch chapters** that fork from specified paragraphs in 10 canon chapters and run to alternative endings. ~65,000 new words.
2. **Forest Edition HTML** — a single self-contained file presenting canon + branches with a split-flap (airport-board) animation that rewrites paragraphs when a branch is selected. Branches persist via localStorage. One branch active at a time.

Branches are *local* in this phase — they change only their own chapter, not downstream world state. The terminal trajectory (b5-reset extending forward through Beats 6–10) is **deferred** to a later phase.

## Spine

`ledger.md` is the source of truth. If anything in any other file conflicts with the ledger, the ledger wins.

## Reading order for any new session

1. **This file** (`CLAUDE.md`).
2. **`STATUS.md`** — current phase, per-branch status, open decisions, recent test runs.
3. **`ledger.md`** — at minimum §1–4. If working on a specific branch, also Part 6 entry for that branch.
4. **`process/voice-profile.md`** — drafters and reviewers must read in full.
5. **`process/architectural-threads.md`** — drafters and reviewers must read in full.
6. **`process/workflow.md`** — the per-branch flow, drafting order, parallelism rules, web cadence.
7. **`process/quality-gates.md`** — concrete definitions of done for each work product.
8. **`process/agent-roster.md`** — what each agent does, what they read, what they don't do.

## Folder map

```
recognition-forest/
├── CLAUDE.md                           ← this file
├── STATUS.md                           ← live status
├── ledger.md                           ← the spine (source of truth)
├── claude-code-opening.md              ← original directive (kept for reference)
├── .claude/agents/                     ← 9 agent system prompts
├── canon/                              ← 10 locked canon drafts (do not edit)
├── bible/                              ← story bible v23
├── branches/beat<1-10>/                ← branch markdowns (drafters write here)
├── process/                            ← working documents
│   ├── voice-profile.md
│   ├── architectural-threads.md
│   ├── agent-roster.md
│   ├── branch-template.md
│   ├── workflow.md
│   ├── quality-gates.md
│   └── decisions.md
├── build/                              ← build.py + recognition-problem.html
└── prototype/index-v4.html             ← base for HTML/animation/branch-logic
```

## Hard rules

- **Do not change canon.** Canon chapters are locked.
- **Embodiment rule (Beats 6–10):** no AI motion across open space. The AI is ambient attention, memory, environmental modulation, coordination. Specialised single-purpose machines do what they're built to do *inside their own enclosures*. No jar glides forward. No cupboard opens on its own.
- **11ms motif duration is canonical.** Branches do not change it.
- **Central entity continuity:** the same continuous system since 2026 across all chapters. The Copy (CAGE-EC-7) is the only entity-fork in canon.
- **Gap-in-the-data thread:** the AI never knows everything about a character. Branches must not close this.
- **Voice continuity is the project's primary integrity.** A branch that doesn't sound like the same author on a different day is broken — regardless of plot quality.
- **Story divergence (ledger §2.1).** A branch must produce a chapter that feels *substantively* different from canon — events that differ from canon, not just content that differs from canon. Late-fork branches are most at risk. The architectural-consistency-checker runs this as item 12 (see `process/architectural-threads.md` §B.6); FAIL is automatic SEND BACK. *Added 2026-05-03 after the b2-kano draft surfaced the gap.*
- **One drafter per branch.** Never one drafter for multiple branches; the per-beat voice context cross-contaminates.
- **Fork paragraph contract:** branch frontmatter `fork_at` must match canon character-for-character. The fork paragraph is the **last shared with the branch** — the paragraph immediately *before* the branch's first divergent paragraph. Build fails on mismatch.

## Workflow at a glance

Per branch:
1. `branch-drafter` produces Draft v1
2. `voice-continuity-checker` + `architectural-consistency-checker` review **in parallel**
3. `coda-specialist` reviews/drafts the coda (skipped for Beat 1 and Beat 7)
4. Orchestrator presents to Rahul
5. Rahul approves (or sends back)
6. On approval: ledger updated → `build-engineer` integrates → `prototype-tester` verifies → `Locked`

SEND BACK from any reviewer returns to drafter; cycle restarts. Cycle 3 with no resolution → escalate to Rahul.

Drafting order across 23 branches: see `process/workflow.md` §2 (four phases — voice-finding, structural complexity, larger-and-harder, largest).

## Parallelism rules

- **Max 2 branches in flight at any time.**
- **Never two branches from the same beat in flight simultaneously.**
- **Max 1 branch awaiting Rahul's review at a time.**
- Voice and arch checkers always run in parallel on the same draft.
- Web work runs in parallel with branch drafting (W1 audit + placeholder build during Phase 2.1; W2 integration once branches lock).

## Communication style with Rahul

- Tight, compressed. Specific questions and recommendations. No padding.
- He gives terse approvals; he doesn't restate context he already has.
- Observations get encoded into project files (voice-profile, threads, agent prompts), not re-stated in chat.
- "Let's proceed" means continue executing.
- UX/UI decisions always go through Rahul. Engineering agents propose; Rahul decides; then implement.

## What this phase is NOT doing

- The terminal trajectory (`b5-reset` extending forward through Beats 6–10). Deferred.
- Any change to canon.
- Drafting branches before Phase 1 is approved.

## Where things live

- **Per-branch reviewer notes:** appended inside the branch markdown's `## Review log` section.
- **Decisions Rahul has made:** logged in `process/decisions.md` (rolling).
- **Test runs after each integration:** appended to `STATUS.md`.
- **Voice and architectural learnings:** appended to `process/voice-profile.md` and `process/architectural-threads.md` as they emerge in review.

## Phase

- **Phase 1** — brainstorming and setup. Steps 1.1–1.7. Status in `STATUS.md`.
- **Phase 2** — parallel execution: drafting branches + building the website. Cannot start until Rahul approves Phase 1.
- **Phase 3** (later) — terminal trajectory.
