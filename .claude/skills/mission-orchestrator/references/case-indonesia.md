# Worked example: Indonesian higher-education workbook with a beach flag

**Mission:** every Indonesian institution serving ages 17–25 (S1, D3 or D4 programs), with its city and province, plus a per-city flag for a real sea beach. Deliverable: a 2-sheet xlsx.

**Result:**
- 4,261 institutions across 444 cities, all 5 gates passed, spot-check 20/20.
- It took about 10 user turns and roughly 1.5M tokens, including 12 research agents.
- An efficient run would need 2–3 turns and about 0.5M tokens.

## What happened, and what should have happened
| # | What happened | Cost | Should have been | Rule |
|---|---|---|---|---|
| 1 | Designed the whole pipeline around the PDDikti API before testing whether it was reachable. It was blocked by Cloudflare. | rewrite of 2 stages | Probe every candidate host first, then design | Scout before build |
| 2 | Wrote "run locally" code, then the user wanted it run in the cloud | 1 turn | Ask in the brief who runs the work and where | Brief: execution venue |
| 3 | The cloud network was blocked, so the user changed the network policy | 1 turn (unavoidable) | Preflight in Stage 1, giving one user step with a verifier | Environment preflight |
| 4 | Overlooked a data portal listing all institutions and programs (dataset IDs 5 and 6) | about 20 minutes | Enumerate the portal's dataset IDs during the probe; it takes 2 minutes | Scout: list the whole catalogue |
| 5 | The count gate failed at −2.56% against the 2% tolerance | 1 stop (legitimate) | Same stop, but raised in the same turn as other predictable issues | Batch the stops |
| 6 | The "no blank city" gate passed even though 36 rows said "Lainnya" ("other") | discovered late, in Stage 4 | A placeholder scan in the Build gate: "Lainnya", "-", "Other", "N/A" | Gatekeeper: placeholder check |
| 7 | City names didn't match OSM: missing Kota/Kab prefixes, regencies renamed since 2005–2020, OSM typos | 3 iterations | Run a match-rate test on the full unique-key list and fix all mismatches in one alias pass | Consolidate: join-rate report |
| 8 | Chose GeoNames as the second source without checking coverage (99 beach points for a whole country) | 1 iteration | Count the second source's coverage before adopting it | Scout: coverage count |
| 9 | Assumed OSM beach tags were complete. A 20-city check gave 13/20 | full Stage 4 rework | Measure recall on 20 sample items before the bulk run | Sample before scale |
| 10 | 8 agents each assumed a full search budget and shared the 200-per-turn cap; 44 rows came back unverified | 1 extra turn | Batch size = budget ÷ (searches per item × safety factor of 1.5) | Swarm: budget maths |
| 11 | Agents answered from memory once the budget ran out | 44 rows needed re-verifying | The evidence contract requires "UNVERIFIED" when a row has no URL, and those rows are never shipped | Swarm: evidence contract |
| 12 | Background `pkill -f` killed its own shell twice; an edit was lost when a combined command was killed | about 15 minutes | Kill processes by PID only, and never chain an edit with a kill | Orchestrator hygiene |
| 13 | Stopped mid-turn to ask about a decision that could have waited (Stage 2 kept going fine) | 1 turn | Stop only when confidence is low; otherwise log and continue | Confidence-gated stop |

## Efficient replay (target: 2–3 turns)
1. **Turn 1, Brief and Plan.** Run the interview: outcome, venue, tolerances for the known risk classes (count tolerance, unlocatable rows, how strict "beach" is). Preflight the hosts. Plan with the method ladder:
   - code for joins and normalization;
   - OSM for inland "no" verdicts;
   - agents for coastal cities, about 280, at ≤8 searches per batch.
2. **Turn 1 (same turn), Probe.** List the portal's catalogue and test samples from the portal files and OSM. Measure OSM beach recall on 20 coastal cities. It is about 50%, so plan agents for every coastal city.
3. **Turn 1–2, Build.** Code pipeline: download, join on code, filter by level, normalize with aliases, flag duplicates. Run the placeholder scan and the join-rate report.
4. **Turn 2, Fill residue.** Research the coastal cities in budget-sized batches. Any rows left over spill into the next turn, planned in advance.
5. **Turn 2–3, Verify and Deliver.** An independent spot-check agent, then the workbook, read-back and report.
