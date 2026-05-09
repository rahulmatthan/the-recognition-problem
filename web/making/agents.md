> *Skeleton.*

## How Claude Code worked

*Two paragraphs. The setup: Claude Code as orchestrator; nine specialised agents (drafter, voice-continuity-checker, architectural-consistency-checker, coda-specialist, build-engineer, prototype-tester, branch-logic-engineer, animation-engineer, html-css-architect); a workflow that gated each branch through review before lock.*

> From `process/workflow.md`, per-branch flow:
> *(1) branch-drafter produces Draft v1; (2) voice-continuity-checker +
> architectural-consistency-checker review in parallel; (3) coda-specialist
> reviews; (4) orchestrator presents to me; (5) I approve or send back;
> (6) on approval: ledger updated → integrate → test → Locked.*

## What worked

*Short list:*

- *The voice profile and architectural threads as agents' read-before-drafting context — agents don't drift if the spec is in front of them.*
- *Pre-emptive naming of flagged risks: when a drafter explicitly addresses an architectural concern in the prose, reviewers credit it.*
- *Parallel reviewers. Voice and architecture are different concerns; one agent can pass the other can fail; running them sequentially would have hidden that.*

## What didn't work, until it was changed

*Short list:*

- *Subagent watchdog cascades on long branches — switched to orchestrator-direct drafting after several timeouts.*
- *Multi-section span at runtime — deferred fix to website rebuild.*
- *Autonomy of the drafter on architectural divergence: needed a specific story-divergence test (added after b2-kano).*

## The role I kept

*One paragraph: what I did, what the agents did. I held the spine — the ledger, the voice profile, the architectural threads, the test for divergence. I drafted the brief, defined the constraints, decided when to send back. The agents drafted prose and ran reviews. I read every branch and approved or rejected each. Nothing locked without me.*
