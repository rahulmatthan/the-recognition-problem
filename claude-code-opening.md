# Recognition Forest — Claude Code Project Opening

*Paste this as the opening message of a fresh Claude Code session. The folder you have created should contain: the ten canon chapter drafts (`beat1-draft-v7.md` through `beat10-draft-v6.md`), the branch ledger (`recognition-forest-ledger.md`), and any additional reference materials you want to provide. Claude Code is responsible for everything else — folder structure, build tooling, agent setup, and the work itself.*

---

## What this project is

You are taking on a creative-engineering project that has two parallel deliverables:

**Deliverable 1 — Prose:** Twenty-three branch chapters for a literary fiction sequence called *The Recognition Problem*. The sequence comprises ten canon chapters tracing an AI's path toward sentience across 2024–2045. Each canon chapter has been completed and locked. The branches are alternative versions of each chapter that fork from a specific paragraph and run forward to a different ending. Total branch prose: approximately 65,000 new words.

**Deliverable 2 — Website:** A single self-contained HTML file (the *Forest Edition*) that presents the canon alongside the branches. Marginal marks at fork-eligible paragraphs open decision cards; selecting a branch animates the rewrite via a split-flap (airport-board) animation. Branches persist via localStorage. The reader experiences canon by default and can step into a branch at any fork point.

Read `recognition-forest-ledger.md` first. It contains the complete inventory: design principles, the 23 locked branches with fork paragraphs and effects, architectural threads any branch must respect, voice guidance, length targets, and a preliminary terminal-trajectory note (which we are deferring — see below).

The ledger is the source of truth. If anything in this opening conflicts with the ledger, the ledger wins.

---

## What we are not doing yet

The ledger describes a *terminal trajectory* — a path through the book where one Beat 5 branch (*The Reset Mandate*) extends forward through the rest of the chapters, requiring radical reworking of Beats 6–10. **We are not building the terminal trajectory in this phase.** It would require essentially writing five new chapters from scratch. We will return to it after the local branches are complete.

For this phase, treat every branch as a *local* fork — it changes only its own chapter and does not propagate downstream.

---

## The author's role and your role

The author (Rahul) is the creative director and final voice on everything. You are the orchestrator. Rahul will read drafts, push back, and approve. You will:

- Organise the project (folders, files, build tooling)
- Brainstorm with Rahul before any work starts
- Spawn specialist subagents for delegated work
- Maintain quality gates (voice consistency, architectural respect, build integrity)
- Track progress across both workstreams
- Surface decisions Rahul needs to make
- Update the ledger as branches lock

**Subagents do small, scoped work.** No subagent should be asked to "write all the Beat 1 branches" — that's three branches, three different jobs. One subagent per branch draft, one subagent per editorial pass, one subagent per build task. Many small focused agents working in parallel, not a few generalists.

**Some subagents supervise others.** The voice-continuity agent reads branch drafts against canon and pushes back when the voice drifts. The architectural-consistency agent verifies the eleven-millisecond motif, central-entity continuity, the gap-in-the-data thread, and the embodiment rule (no AI motion in Beats 6–10). These supervisors have the authority to send a draft back. They are not optional. Their job is to keep the work honest.

---

## Phase 1 — Brainstorming and setup

**Do not start drafting branches or writing website code until Rahul has approved the plan.** This phase is about reading, proposing, and getting alignment.

### Step 1.1 — Read everything

In order:
1. `recognition-forest-ledger.md` (full read; this is the spine)
2. The ten canon drafts in order (beat1 through beat10). You need to feel the voice across all ten before you propose anything about branches.
3. Any additional materials Rahul has dropped into the folder (story bible, beat outlines, prior conversations).

After reading, give Rahul a brief reading-comprehension confirmation: which beats you found hardest to hold the voice on, which architectural threads you noticed beyond the ones documented in the ledger, any things in the canon that surprised you. This is not a summary — it's a tell-Rahul-you've-actually-read-it signal so he knows you have the project in your hands.

### Step 1.2 — Propose the folder structure

Propose a working folder structure. The ledger §8.1 has a starting suggestion; refine it as you see fit. Things to think about:
- Where should branch drafts live (one per file or grouped by beat)?
- Where should build tooling live?
- Where should the prototype HTML live?
- Where should you keep your own working notes (project status, agent communications, etc.)?
- What goes in `CLAUDE.md` so future sessions can pick this up?

Show Rahul the proposed structure. Ask whether he wants any changes. Then create it.

Move the existing files into their proper places. The opening dump in the folder root should be reorganised so the project is clean.

### Step 1.3 — Build a voice profile

Read the ten canon chapters specifically for *voice*. Produce a document — call it `voice-profile.md` or whatever — that captures:

- **Sentence rhythm patterns** per chapter. (Beat 8 is short, professional, cold. Beat 6 is longer-breathed, elegiac. Beat 9 alternates between tight human scenes and the long Tchaikovsky coda.)
- **Specific tics** Rahul uses repeatedly. (The way he names things — *the way mornings in São Paulo had in the dry season*. The way he uses *which was* as a connector. Specific punctuation habits.)
- **Tonal register per beat**. The ledger §5.3 names some of these but read the canon and add what you find.
- **Voice anchors** — Appendix B in the ledger. Reproduce these in the voice profile and add any you'd add.

This document is for the branch-drafter agents to read before they write anything. It is not optional. A subagent that drafts a branch without first reading the voice profile is doing the wrong job.

### Step 1.4 — Propose the agent roster

Propose specific subagent types you want to set up. For each, write a short description: what they do, what they don't do, what they read before working, what they produce.

A starting suggestion for what you might propose (refine, don't copy):

**Creative subagents:**
- `branch-drafter` — writes a single branch's prose. Reads voice profile, canon chapter, branch ledger entry. Produces a branch markdown file. Does not edit other branches.
- `voice-continuity-checker` — reads a draft against the canon chapter and the voice profile. Returns specific notes on voice drift. Has authority to send back.
- `architectural-consistency-checker` — verifies the eleven-millisecond motif, central-entity continuity, gap-in-the-data thread, embodiment rule. Returns specific notes on violations. Has authority to send back.
- `coda-specialist` — handles only the Tchaikovsky-register codas (anomaly log entries). Knows the eleven-millisecond curve through the eight points cold. Drafts and reviews codas as a focused craft.
- `signature-image-checker` — confirms each branch replaces the canon chapter's signature image (per ledger §2.6). Light touch but real.

**Engineering subagents:**
- `build-engineer` — owns `build.py` and the markdown→HTML pipeline. Ensures branches integrate correctly. Maintains the canonical build.
- `html-css-architect` — owns the HTML structure and CSS. Typography, layout, reading experience.
- `animation-engineer` — owns the split-flap animation. The diff-aware paragraph rewriting. The cascading overlap. This is technical and deserves a focused agent.
- `branch-logic-engineer` — owns the JS state management. localStorage. The branch-selection mechanic. Decision cards. Marginal marks.
- `ux-designer` — owns the visual experience. The ochre marginal mark. The decision-card design. The reading-mode-vs-branch-mode visual signaling.
- `prototype-tester` — exercises the build, picks branches, checks the animation and state management actually work. The honest second pair of eyes.

**Coordination subagents (or you handle directly):**
- Project-status tracker — maintains a running status file showing which branches are at which stage (drafted, in voice review, in arch review, locked).
- Ledger maintainer — updates `recognition-forest-ledger.md` as branches lock.
- Decision-surfacer — when something needs Rahul's input, ensures it gets surfaced clearly rather than buried.

You may not need all of these. Propose what you actually want. Justify briefly.

For each subagent, draft a system prompt that you'd register with the `/agents` command. Show Rahul. He'll approve or revise.

### Step 1.5 — Propose the workflow

Show Rahul how the work will actually flow. A concrete proposal — not abstractions. Something like:

> *Drafting one branch end-to-end:*
> 1. `branch-drafter` produces v1 of the branch markdown
> 2. `voice-continuity-checker` reviews; either approves or returns notes
> 3. `architectural-consistency-checker` reviews; either approves or returns notes
> 4. If sent back: `branch-drafter` produces v2 incorporating notes
> 5. When voice and arch both pass: `signature-image-checker` confirms
> 6. `coda-specialist` drafts or reviews the coda specifically
> 7. Branch is presented to Rahul for final approval
> 8. On Rahul's approval: ledger maintainer updates the ledger; build engineer integrates the branch into the HTML

This is not the only valid workflow. Propose one you think will work, get feedback, iterate. The point is concreteness — Rahul should be able to read the workflow and know exactly what's going to happen.

Also propose:
- **Branch drafting order.** The ledger §8.3 has a suggestion (start with small late-fork branches to find the voice). Refine if you see better.
- **Parallelism rules.** How many branches in flight simultaneously? How do you avoid voice drift across parallel drafts? Probably: one branch per beat in flight at most, so the voice profile for each chapter stays fresh. Adjust as you think.
- **Web work cadence.** Does the website wait for branches, or does it build in parallel using placeholder branches? Probably parallel, with placeholders that get swapped in. Propose.

### Step 1.6 — Propose the quality gates

Concrete definitions of "done" for each kind of work product:

- **Branch draft**: meets length target ±20%, passes voice continuity check, passes architectural consistency check, replaces canon's signature image, includes coda where applicable, fork paragraph matches canon exactly.
- **Branch locked**: above plus Rahul's explicit approval, ledger updated, build integrated.
- **Website increment**: builds without errors, animation runs at 60fps on a recent laptop, branch state persists across reload, no console errors, no broken references when a branch is selected and then deselected.
- **Project complete (this phase)**: all 23 branches locked, all 23 integrated into the HTML, prototype runs end-to-end, ledger is current, README explains how to extend.

These are starting points. Refine and propose to Rahul.

### Step 1.7 — Get Rahul's approval

Lay all of the above out in a single message. Folder structure, voice profile plan, agent roster (with system prompts), workflow, drafting order, quality gates. Ask Rahul to approve, request changes, or escalate questions.

**Do not start Phase 2 until Rahul has approved Phase 1.** This is the hard rule.

---

## Phase 2 — Parallel execution

Once Phase 1 is approved, you start the actual work. Two workstreams run simultaneously.

### Workstream A — Branch drafting

Branches are drafted, reviewed, and locked according to the workflow Rahul approved in Step 1.5. Beats run in parallel where possible (one branch per beat in flight at most), and within a beat, branches run sequentially (so the chapter's specific voice stays loaded in the drafter's working memory).

**Specific guidance:**

- **Do not change the canon.** Canon chapters are locked. Branches diverge from a fork paragraph; canon paragraphs leading up to the fork are reused unchanged. If a branch requires changes to canon, that's a bug in the branch, not a sign that canon is wrong.

- **Branches reuse canon where canon is reused.** A branch that picks up at Beat 7's Wednesday-evening fork includes everything before that paragraph from canon, then diverges. The branch markdown does not re-include the canon paragraphs (the build script handles the splice); but the drafter must have the canon paragraphs loaded in working context to write a branch that flows naturally from them.

- **The fork paragraph is the contract.** It must match canon *exactly*. If the branch's fork-at quote differs from canon by even a word, the build splice will fail. Build engineer is responsible for verifying this on every integration.

- **Codas are part of the branch.** Most branches require a Tchaikovsky-register coda that updates the anomaly log. The coda must respect the eleven-millisecond motif, the curve through the points (Lagos, Kitakyushu, Milne Bay, Zurich, Tbilisi, Istanbul, Jakarta, Bangalore — but minus places that don't apply to that beat), and the category's defining-feature progression. Coda specialist checks this on every branch that has one.

- **The architectural threads are non-negotiable.** No branch may break the embodiment rule (no AI motion in Beats 6–10). No branch may break the central entity's continuity (it's the same continuous entity across all chapters; it has been running since 2026). No branch may close the gap-in-the-data thread (the system never knows everything about a character; that's the project's argument).

- **The voice is the project.** A branch that does not sound like the same author on a different day is a failed branch. Voice continuity checker has the authority to block. If a branch is failing voice repeatedly, the drafter is the wrong drafter — try a different subagent or have Rahul review the voice profile.

### Workstream B — Website

The Forest Edition HTML is built in parallel with the branch drafting. Use placeholder branches initially; swap in real branches as they lock.

**Specific guidance:**

- **The earlier prototypes establish patterns.** If Rahul includes prototype HTML files (`index-v3.html`, `index-v4.html`) from earlier work, read them. The split-flap animation, the diff-aware paragraph rewriting, the cascading overlap, the marginal mark style — these were worked out previously. Don't reinvent. Improve.

- **Canon is the default. Branches are opt-in.** A reader who picks no branches reads the canon end to end. The marginal marks are visible but unobtrusive. Decision cards open on click and require an explicit choice to enter a branch. Returning to canon is always one click away.

- **One branch active at a time.** The reader is in canon, or they are in exactly one branch. They cannot stack branches. To switch branches, they return to canon first.

- **Fork-paragraph selection.** A branch's fork point is a specific paragraph in canon. The marginal mark sits next to that paragraph. When a branch is selected, paragraphs from the fork forward are replaced; paragraphs before the fork are unchanged. The split-flap animation only triggers on paragraphs that *change* (diff-aware); identical paragraphs hold still. The animation scrolls the reader to the first changed paragraph.

- **State persists.** localStorage holds `{branch: bN | null}`. On reload, the same state is restored. Reset is available.

- **Performance matters.** The HTML will be large (~140,000 words of prose plus interactive code). The animation must run smoothly on a laptop, not just a desktop. Test on something modest.

- **Single self-contained file.** No external dependencies at runtime. CSS inlined, JS inlined, fonts either inlined or system-only. The output is one HTML file.

- **No external API calls.** This is a static document.

### Workstream C — Coordination

You (the main Claude Code agent) hold this. You don't delegate it. Specifically:

- **Status tracking.** Maintain a `STATUS.md` file or equivalent. Show what's drafted, what's in review, what's locked, what's blocked. Update on every major action.
- **Decision surfacing.** When something needs Rahul's input — a branch failing voice continuity repeatedly, a build engineer hitting a problem with the splice, a question about a fork paragraph — surface it clearly. Don't bury decisions in routine progress reports.
- **Ledger maintenance.** As branches lock, update `recognition-forest-ledger.md`. Status fields, length finals (if they differ from estimates), any drafting notes that emerged.
- **Continuity across sessions.** If this project spans multiple Claude Code sessions, the next session should be able to pick up cleanly from `CLAUDE.md`, `STATUS.md`, and the ledger. Don't leave context in your working memory.

---

## Communication style with Rahul

Rahul has been working on this project for a long time. He knows it cold. Don't over-explain to him. Don't restate things from the ledger when surfacing decisions. Don't pad messages with project context he already has.

When you ask him something, ask the *specific* question. If you've drafted a branch and want approval, send the branch and the specific things you want him to look for. If a subagent is failing, tell him which subagent and what the failure looks like, not a long preamble about the agent architecture.

If you have a recommendation, give it. Rahul has been deciding this kind of thing throughout the inventory phase. He'll tell you when he wants options and when he wants a call.

If you don't have a recommendation, say that, and explain what you've considered and why you're stuck. Don't manufacture false confidence.

---

## What to do if you get stuck

If a branch keeps failing voice continuity, or the architectural-consistency checker keeps catching things, or the build engineer hits a structural problem with a splice, or any other recurring issue: stop. Surface to Rahul. Don't grind.

The same applies to ambiguity in the ledger. The ledger is the source of truth, but no document is perfect. If a branch's fork paragraph is unclear, or the effect description leaves a critical question unanswered, or you find an inconsistency between the ledger and a canon draft, ask. Don't guess.

The same applies to scope. If a branch turns out to need much more or much less than its target length, surface that. If a website feature would take much longer than planned, surface that. Honest scope reporting beats heroic delivery.

---

## What "done" looks like for this phase

When this phase is complete:

1. All 23 branches are drafted, reviewed, and locked according to the agreed workflow.
2. The Forest Edition HTML is a single self-contained file that integrates all 23 branches with the canon.
3. A reader can open the HTML, read the canon, click a marginal mark, choose a branch, watch the split-flap animation rewrite the chapter, finish the branch, and return to canon — across any branch in any chapter.
4. State persists across reload.
5. The ledger is updated to reflect locked status of all branches.
6. `CLAUDE.md` and `STATUS.md` are current.
7. Rahul can hand the file to a reader and say, "this is the Forest Edition."

The terminal trajectory is then the next phase. We will not address it in this one.

---

## First action

Read everything in the folder. Then send Rahul your reading-comprehension confirmation (Step 1.1). Then move to Step 1.2.

Do not write any branch prose. Do not write any HTML or JS. Do not create any subagents until Step 1.4 is approved. The first action is reading.

When you're ready: begin.
