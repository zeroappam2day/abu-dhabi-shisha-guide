---
name: mission-orchestrator
description: Entry point for any mass-research mission that must end in one consolidated, accurate output (a dataset, workbook, ranked list or merged spreadsheet). Examples include an institution census with a geographic flag, a stock screen, a recipe shortlist, or reconciling several spreadsheets. Use when the user describes such a mission, or says "mission", "research and consolidate", "build me a list of all X with Y". It runs a fixed stage spine and routes each stage to the mission-* skills.
---

# Mission Orchestrator

Run every mass-research mission through one fixed spine. Each stage calls a role skill and ends at a gate. Do not improvise the order.

## Stage spine
| # | Stage | Skill to load | Exit condition |
|---|---|---|---|
| 0 | Brief | `mission-brief` | Brief approved ("go") |
| 1 | Plan | `mission-plan` | Plan with tool-call and budget ledger written |
| 2 | Probe | `mission-source-scout` | Every planned source tested on a sample; winners recorded |
| 3 | Build | `mission-consolidate` | Code pipeline produces the base table; gate passes |
| 4 | Fill residue | `mission-research-swarm` (only if a residue exists) | Every residue row has a verdict with evidence |
| 5 | Verify | `mission-gatekeeper` | Independent spot-check meets its threshold |
| 6 | Deliver | `mission-deliver` | Artifact read back, report written, published or committed |

`mission-gatekeeper` also runs at the end of stages 2–4. Load each skill only when its stage starts.

## Operating rules
1. **Plan before acting.** No tool call that the plan in `mission-plan` does not foresee. If reality diverges, re-plan explicitly with a one-line reason, then continue.
2. **Small sample before scale.** Any source, method or assumption is tested on about 10–20 items before it touches the full set. This rule alone would have prevented most of the rework in `references/case-indonesia.md`.
3. **Cheapest reliable method first:** code → structured source → tool → existing skill → research agent. Agents only handle the residue that cheaper methods cannot resolve.
4. **Confidence-gated stops.** Proceed when the gathered evidence supports the answer, and log the decision. Stop and ask when it does not; `mission-gatekeeper` defines the signals. Put all open issues into one stop.
5. **State on disk.** Keep `mission/STATE.md` (template in `references/templates.md`) holding:
   - the current stage;
   - decisions;
   - the budget ledger;
   - open issues.

   Update it at every stage exit, so a restart or context loss costs nothing.
6. **Commit at every gate pass** when working in a repository, so an ephemeral environment cannot lose work.
7. **Never fabricate.** Any value without evidence is marked unverified. It is never shipped as verified.

## Environment preflight (run once, in Stage 1)
Check these with a single batched command:
- reachability of each planned host;
- disk space and RAM for large downloads;
- the search budget per turn (the default cap is 200 searches per turn, shared across agents);
- available Python libraries.

Record the results in the plan. A blocked host is a user step: give the exact step plus how to verify it.

## Response style
- At stage exits, a status line: Done / Current / Next.
- User-facing steps are numbered, each with a verifier, with no preamble.
- The final message gives the results, decisions and caveats, then stops.

## References (read only when needed)
- `references/case-indonesia.md`: the worked example. A 10-turn run, with what each turn should have been.
- `references/templates.md`: STATE.md, the budget ledger, the gate log, the evidence CSV contract and the agent prompt.
