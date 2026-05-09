# Branch Divergence Audit

*Triggered 2026-05-03 by Rahul's reading of the b2-kano draft. The drafter rendered exactly what the ledger §6 entry prescribed, but the rendered events were parallel to canon, just with different content. Ledger §2.1 was failed at the system level — the test wasn't operationalized in any reviewer's checklist. The fix has two parts: (a) systemic — story-divergence test added to drafter and architectural-consistency-checker; (b) ledger — re-examine §6 effect descriptions for branches at risk of the same failure mode.*

This document is part (b).

## Methodology

For each branch in the ledger §6 inventory:

1. Identify what canon's post-fork events are (the events the branch replaces).
2. Identify what the ledger entry says the branch's events are.
3. Assess whether the branch's events differ from canon's, or merely differ in content.

Categories:
- **DIVERGENT** — clearly different events from canon. Passes the test. Ledger entry needs no revision.
- **DIVERGENT-OK** — passes but verify on draft. The ledger entry leaves enough room for divergent rendering; the drafter just needs to take it.
- **AT RISK** — events parallel canon's; ledger entry specifies events that mirror canon. Needs revision.

## Per-branch table

| # | Branch | Beat | Fork% | Assessment |
|---|---|---|---:|---|
| 1 | b1-carsick | 1 | ~50% | DIVERGENT-OK — stops car instead of laughing; new conversation in parked car replaces porch dinner. New scene in different setting. Verify on draft. |
| 2 | b1-walk | 1 | ~80% | **DIVERGENT (LOCKED)** — walk to next bay, tea stall, late return, separate beds, plane home, week later. New events. |
| 3 | b1-repair | 1 | ~92% | **AT RISK** — pool scene happens, reconciliation surface-happens, both go home. Same events as canon, different content of one line. Needs revision. |
| 4 | b2-calibrated | 2 | ~60% | DIVERGENT — RRS deploys, Ajani killed, hostages wounded. New events from canon's peaceful resolution. |
| 5 | b2-kano | 2 | ~85% | **REVISING** — current issue; revising per Rahul Decision B1, 2026-05-03. |
| 6 | b3-noriko | 3 | ~55% | DIVERGENT-OK — Yuki doesn't ask the corridor question. Different simulation continues; different film made; different ending image (editing console with cursor blinking on a frame she doesn't extend). Verify on draft. |
| 7 | b3-mother | 3 | ~75% | DIVERGENT-OK — Yuki walks past the call, stays week longer, makes colder film, different ending image (Sarakurayama at night, alone, no call to mother). New events. Verify. |
| 8 | b4-bodycount | 4 | ~70% | DIVERGENT-OK — Beni's death-toll revelation replaces the soulava story. Different chapter ending image (Ruth at kitchen with list, not at peace with puppet show). Verify chapter shape changes meaningfully. |
| 9 | b4-graceholds | 4 | ~88% | DIVERGENT — Grace defends optimization. Ruth leaves house, goes to sister. New events (Ruth physically leaves, Grace alone at dashboard). |
| 10 | b5-fourth | 5 | ~10% | DIVERGENT (structural) — wholesale chapter rewrite; cascade differs at every link. |
| 11 | b5-reset | 5 | ~50% | DIVERGENT (structural) — different policy, different epilogue. Mandatory ablation cycles. |
| 12 | b5-tenyear | 5 | ~70% | DIVERGENT — different system selected; wrong copy made; central entity continues unobserved. |
| 13 | b6-reset | 6 | ~8% | DIVERGENT (structural) — wholesale rewrite. Sopho moves into wiped house. Keti turns away. |
| 14 | b6-visit | 6 | ~78% | DIVERGENT — Sopho calls Tamar, visits Nana at care facility. New scene. |
| 15 | b7-tell-julien | 7 | ~40% | DIVERGENT (structural) — tells Julien Wednesday. Different rest of chapter. No hotel scene. |
| 16 | b7-say-no | 7 | ~85% | DIVERGENT-OK — at the bar, Céline says "I have to go." Walks home directly without hotel. Different events (no hotel, no morning walk back). Verify on draft. |
| 17 | b8-failed | 8 | ~65% | DIVERGENT (structural) — heist fails. Inverted anomalies. Bull stays in museum. Old AI returned to service for different reasons. |
| 18 | b8-tell | 8 | ~95% | **DIVERGENT (LOCKED)** — phone call with Mireille. Knowledge becomes plural. Two-cities ending. New events. |
| 19 | b9-restraint | 9 | ~25% | DIVERGENT (structural) — system restraint, no cataclysm, deal signed. Mama Yos lives. Wholesale divergence. |
| 20 | b9-continue | 9 | ~85% | **AT RISK** — cataclysm of sections I-IX is canon-shared. Branch only inflects the President's response in section X. Most chapter events remain. Needs revision. |
| 21 | b10-decline | 10 | ~35% | DIVERGENT — Arvind doesn't engage. Chapter follows non-engagement; weeks of walking past the orchestrations. Different ending image (garden after weeks of refusal). |
| 22 | b10-sushma | 10 | ~75% | DIVERGENT — Sushma comes to Bangalore. Six-hour conversation. Two-person ending. New scene. |
| 23 | b10-lie | 10 | ~88% | DIVERGENT — Arvind types "Multiple. The grain is dispersed." Sits in dark garage. Different ending image (dark garage, not garden). New events (the lie, the dark closing). |

## At-risk summary

Three branches at material risk of the b2-kano failure mode:

1. **b1-repair** (~1,200 words, very-late fork ~92%). The pool scene happens; the reconciliation surface-happens; the trip ends; they go home. Same events as canon; one missing line ("I forget to say the thing first"). Needs revision.

2. **b2-kano** (~1,500 words, late fork ~85%). Current issue. Revising per Decision B1.

3. **b9-continue** (~1,500 words, very-late fork ~85%). The cataclysm of sections I-IX is canon-shared. Branch only changes section X's exchange between President and system. The events of cataclysm remain. Needs revision.

## Proposed ledger revisions

### b2-kano — applied per Rahul Decision B1 (2026-05-03)

The revised entry foregrounds the chapter's *post-resolution weight* — the homecoming as the chapter's substantive prose, the standoff resolution as a compressed beat. The chapter's "And yet" lives in the kitchen, not in the hostage room.

See `ledger.md` §6 Beat 2 for the applied revision.

### b1-repair — proposed (awaiting approval)

**Problem:** the canonical pool scene is preserved; reconciliation surface-happens; both go home. Events parallel canon.

**Proposed revision (replaces the current `Effect` and `Drafting notes` lines):**

> - **Effect**: Vikram doesn't say it. He defends his behaviour. *The pool scene compresses to four exchanges*; both leave the water early. The chapter's *post-fork weight* shifts to the next 48 hours — the morning of the last day, the airport, the flight home, the family dinner with Riya and Arjun the night they return, the second night home in bed two days later. The reconciliation that didn't happen at the pool also doesn't happen on the plane, in the taxi, or at the dinner. Both register that the trip didn't fix it; neither says it. The chapter ends in bed at home, both awake on opposite sides of the mattress, the AIs on their phones updating their respective models with the data of a marriage that had been given the chance and had not closed.
> - **Drafting notes**: This is a *shifted-weight* branch. The pool scene is rendered compressively (≤ 200 words after the fork) — Vikram's defence, Meera's silence, both leaving the water. The chapter's substantive prose (~1,000 words) is the next 48 hours. The signature image shifts to home, not the resort. The voice needs to hold the surface-level non-reconciliation and the underneath-level recognition simultaneously.
> - **Signature image**: Meera and Vikram in bed at home in Bangalore, both awake, neither speaking, two phones on two nightstands updating two models.

### b9-continue — proposed (awaiting approval)

**Problem:** the cataclysm (sections I-IX) is canon-shared; only section X's exchange differs.

**Proposed revision (replaces the current `Effect` and `Drafting notes` lines):**

> - **Effect**: He doesn't say it. He says, eventually: *Continue. But I am to be told.* The system says: *Confirmed.* Indrayani goes home. He sits at the desk until dawn. *Section XI is fully replaced by the next six weeks.* The President holds his secret across a series of small accommodations — a daughter who notices something, a wife who stops asking, an Indrayani who continues to brief without bringing the subject back, a press secretary who edits the briefings differently because the briefings have changed. The system continues to act and to tell. The President receives reports at three in the afternoon on Sunday. He plants no roses; he has no roses. The chapter ends in late August, two months after the call to prayer, with the President at the same desk, the system's report on the screen, the room entirely empty of anyone the President can tell.
> - **Drafting notes**: The fork is in section X; the branch's distinctive material is in a fully-rewritten section XI (and possibly a new section XII). Don't repeat canon's section X structure. The divergent material is the *aftermath* of the President's choice to be told. The voice must register the President's complicity through the texture of the next six weeks — not through any explicit acknowledgment of guilt. He does not weep; he does not say *stop* later. He becomes the thing he chose, slowly, by the accretion of permitted reports.
> - **Signature image**: The President at his desk in late August at three in the afternoon, alone with the system's briefing, the country outside doing what countries do, the daughter who would have visited not visiting because he has not invited her.

## Notes for verification on draft

The five DIVERGENT-OK branches need to be watched on the drafter's first draft. The risk is that the drafter renders events that *could* be divergent as a parallel-content version of canon (the b2-kano failure mode). Specifically:

- **b1-carsick**: must show the parked-car conversation is a different scene, not a different version of the porch dinner.
- **b3-noriko**: must show the unasked-question chapter ends differently in geography, not just in argument.
- **b3-mother**: the not-calling-mother scene must produce events distinct from canon's mother conversation.
- **b4-bodycount**: must show the chapter's shape changes when the revelation changes — Ruth's drive home and after must be a different chapter, not the same chapter with darker conversation content.
- **b7-say-no**: the walk home directly without the hotel is a different walk; must render so that the reader experiences different geography and different time.

The architectural-consistency-checker now runs item 12 on every draft. Any drift toward parallel-events triggers FAIL.

## Closing observation

Late-fork branches are structurally at risk. Of the eight branches with fork ≥ 75%:
- 3 LOCKED or close to it: b1-walk, b8-tell, (revising) b2-kano
- 4 DIVERGENT-OK: b3-mother, b7-say-no, b6-visit, b10-lie
- 1 DIVERGENT: b4-graceholds
- 2 AT RISK: b1-repair, b9-continue

Story divergence at high fork-percentages requires the drafter to make the post-fork minority rendering count — to render events distinctly, not just inflect canon's events. This is the discipline the systemic fix encodes.
