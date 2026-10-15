---
name: mission-plan
description: Stage 1 of a mission-orchestrator run. Reverse-engineers an execution plan from the approved deliverable, assigns each step the cheapest reliable method (code, structured source, tool, skill, research agent), runs an environment preflight, and writes a tool-call and budget ledger before any work starts. Use after the brief is approved, or whenever reality forces a re-plan.
---

# Mission Plan

## 1. Reverse-engineer from the deliverable
Start from the final artifact's columns and gates and work backwards: for each column, list what produces it and what that step needs. The result is a dependency chain of steps, each with:
- its input;
- its output;
- its gate check;
- its method.

## 2. Method ladder: pick the cheapest reliable rung
| Rung | Use when | Example |
|---|---|---|
| 1. Code on data you already have | Deterministic transforms such as join, filter, normalize, count, deduplicate | pandas/openpyxl join on code |
| 2. Structured source | An official file, API, or a dataset with the field already present | the ministry's xlsx; an OSM extract |
| 3. Tool | A built-in or MCP tool answers it directly | the Artifact tool, gh, database MCP |
| 4. Existing skill | The format or domain has a skill | xlsx, pdf, data:validate-data |
| 5. Research agent | Only the residue that rungs 1–4 cannot resolve | coastal cities with no OSM beach |

Estimate the residue size before committing to rung 5. Research cost grows with residue size, so shrink the residue with rungs 1–4 first. Example: geometry settles inland cities, leaving only coastal ones for agents.

## 3. Environment preflight (one batched command)
Check:
- HTTP status for every planned host;
- free disk and RAM against the largest download (×3 for processing);
- Python packages;
- the search budget (default 200 web searches per turn, shared by all agents in the turn).

Any blocked prerequisite becomes one user step, with a verifier.

## 4. Tool-call and budget ledger
Write this into `mission/STATE.md`:
- planned calls per stage;
- planned web searches per stage (batches sized by `mission-research-swarm`);
- an estimated token range;
- the planned number of turns (Fill residue may span turns because of the search cap; plan that explicitly).

Over-run rule: if a stage goes past 1.5× its plan, stop, re-plan with a one-line reason, and tell the user if the turn count changes.

## 5. Probe list
For every source and every assumption the plan relies on, add a sample test for `mission-source-scout`. Examples: "OSM tags capture most beaches"; "the address field holds the city".

## Anti-patterns
- Designing code around a source before probing it.
- Using agents for work that code or a structured source can do.
- Leaving the search cap or cross-turn spill unplanned.
