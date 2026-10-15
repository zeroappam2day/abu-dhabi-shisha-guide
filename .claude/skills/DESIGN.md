# Mission skill suite: design record (O-R-G)

## O: Outcome
**Who it's for:** you, or any agent session given a "mass research → one consolidated, accurate output" mission. Examples: an institution census, a stock screen, a recipe shortlist, merging several spreadsheets.

**What they should do after:** run a pre-planned, gated sequence that delivers a correct artifact in the fewest turns, with zero unnecessary tool calls.

**How we know it worked:**
1. Every gate passes, with evidence on file.
2. The final report names every decision and caveat.
3. The run finishes in kickoff + delivery turns (best endeavours). The only extra stops are the confidence-gated ones.
4. Actual tool calls and tokens fall within 1.5× the plan.

## R: Rules from the reverse interview
1. **Deliverable:** a new reusable skill suite, one skill per stage plus an orchestrator.
2. **Scope:** any mass-research → consolidated-output mission.
3. **Install:** a source folder at `.claude/skills/`, plus a zip for claude.ai.
4. **Stop rule:** stop and ask whenever the evidence gathered so far does not support confidence in the answer. Otherwise proceed and log. Do not try to pre-ask every possible failure.
5. **Efficiency:** fewest turns (best endeavours), fewest tokens, zero unnecessary tool calls. Tool calls are planned before execution. The method ladder is: code → structured source → tool → skill → research agent.

## G1: Three different architectures

### A. Stage pipeline
One skill per lifecycle stage: brief, plan, probe, consolidate, research, gate, deliver. The orchestrator runs them in order.

### B. Capability roles
Skills are roles reused across stages: Planner, Scout (finds and tests sources), Swarm (parallel research), Auditor (gates and spot-checks), Scribe (output and report). The orchestrator calls a role whenever any stage needs it.

### C. Single playbook
One skill holds the whole workflow, with reference files per stage, loaded on demand.

## G2: Harsh grading
The test cases are this session's actual failures (`mission-orchestrator/references/case-indonesia.md`). Scores run 0 (fails) to 3 (prevents it).

| Criterion / failure mode | A | B | C |
|---|---|---|---|
| Probing sources before building on them (built for the PDDikti API, then GeoNames, before checking coverage) | 2: has a probe stage, but it runs only once, before Stage 1 | **3**: Scout is invoked wherever a new source appears, including the second source in Stage 4 | 1: easy to skim past |
| Measuring recall on a tiny sample before scaling (assumed OSM beach tags were complete) | 1 | **3**: Auditor runs a sample check before any bulk step | 1 |
| Search-budget-aware swarm sizing (agents hit the 200-searches-per-turn cap) | 2 | **3**: Swarm owns the budget maths | 1 |
| Clear sequence, low cognitive load | **3** | 1: no inherent order; the orchestrator must invent one | 2 |
| Zero unnecessary tool calls / tokens loaded | 2: 7 skill loads | 2 | **3**: one load, refs on demand |
| Reuse beyond this mission type | 2 | **3** | 1 |
| Confidence-gated stops | 2: gates sit only at stage ends | **3**: Auditor is callable anywhere | 2 |
| **Total** | 14 | **18** | 11 |

**Winner: B.** Its remaining weaknesses:
1. Roles have no order, so the orchestrator could improvise and repeat the drift seen in this session.
2. Five or six skill loads cost tokens.
3. Planning (reverse engineering and the tool-call budget) is spread across roles.

## G3: Fixes applied to B (the final design)
1. **A's stage spine goes into the orchestrator.** It holds the fixed sequence Brief → Plan → Probe → Build → Fill residue → Verify → Deliver and says which role each stage calls. That gives B's reuse with A's order.
2. **Thin skills.** Each `SKILL.md` keeps only rules and checklists. Templates and the case study live in `references/` and are read only when needed, which makes token cost similar to C.
3. **One planning owner.** `mission-plan` owns the reverse-engineered plan, the method ladder, the tool-call plan and the budget ledger. Every other skill checks its actions against that plan.
4. **Explicit stop rule** (`mission-gatekeeper`): stop when confidence is low. "Low" is defined by observable signals, not by feel.

## Final suite
| Skill | Role | Stages it serves |
|---|---|---|
| `mission-orchestrator` | Entry point: stage spine, state file, routing | all |
| `mission-brief` | O + R: outcome, success criteria, the one-at-a-time interview | Brief |
| `mission-plan` | Reverse-engineers from the deliverable; method ladder; tool-call and budget plan | Plan; replan |
| `mission-source-scout` | Finds candidate sources and tests each on a ~10-row sample | Probe; any new source |
| `mission-consolidate` | Code-first extract, join, normalize, flag; central config | Build |
| `mission-research-swarm` | Budget-sized parallel agents for the residue only; evidence contract | Fill residue; spot-check |
| `mission-gatekeeper` | Gates, confidence-gated stops, independent spot-check, evidence ledger | after every stage |
| `mission-deliver` | Builds the artifact, reads it back, writes the final report | Deliver |
