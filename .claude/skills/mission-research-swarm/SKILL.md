---
name: mission-research-swarm
description: Stage 4 of a mission-orchestrator run, and also used for independent spot-checks. Resolves only the residue that code and structured sources cannot, using parallel research agents sized to the web-search budget. Every row must carry a URL-backed evidence string or be marked UNVERIFIED. Use when tens or hundreds of items each need a web-verified verdict.
---

# Research Swarm (residue only)

## 1. Shrink the residue first
Only items that rungs 1–4 of the method ladder cannot settle go to agents. Write the residue list to a file. Never send items whose answer is already determined.

## 2. Size the batches to the budget
Budget maths:
- `B` = web searches left this turn (default cap 200, shared by every agent in the turn, including you);
- `s` = searches per item (1–3; use 3 for disambiguation-heavy items);
- capacity this turn = floor(B ÷ (s × 1.5)) items.

How to use it:
- Number of agents = ceil(capacity ÷ 15–20). Keep each agent at ≤20 items so it stays focused.
- Residue beyond capacity goes into **planned** later turns. Tell the user in advance that one reply is needed per batch round.
- Hold back about 10 searches for yourself to fix single stragglers.

## 3. Prompt contract
Use the template in `mission-orchestrator/references/templates.md`. It must include:
- the strict definition, with yes/no criteria, exclusions and disambiguation rules;
- input and output file paths, so agents write files instead of returning bulky text;
- the per-item search cap and "never answer from memory";
- the evidence format `"<claim> - <URL>"`, or a leading `UNVERIFIED`;
- an instruction to reply with the row count plus at most 5 uncertain items;
- no user personal data in queries or headers.

## 4. Merge
- Copy the keys exactly. Normalize any aliases (for example a province rename) before merging.
- A row is `verified=yes` only if it has a URL and is not marked UNVERIFIED. Re-queue unverified rows next turn; never ship them as verified.
- Keep the merged file committed, for example `<attribute>_web.csv`.

## 5. Independence for spot-checks
A spot-check agent is a separate agent with a separate prompt, and it gets no prior verdicts. It checks a seeded random sample chosen by `mission-gatekeeper`.

## Anti-patterns
- Launching 8 agents that each assume a full search budget.
- Accepting answers "from prior knowledge" as evidence.
- Reading agent transcript files into context. Read only their output files.
